"""
Real-time Notification Service for ATLAS Enterprise
WebSocket-based notifications, email alerts, and push notifications.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

import websockets
from fastapi import WebSocket
from pydantic import BaseModel

from ..core.database import get_cache
from ..core.logging import get_logger, log_business_event
from ..core.config import settings

logger = get_logger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    TARIFF_UPDATE = "tariff_update"
    CURRENCY_CHANGE = "currency_change"
    CALCULATION_COMPLETE = "calculation_complete"
    KNOWLEDGE_UPDATE = "knowledge_update"
    SYSTEM_ALERT = "system_alert"
    USER_MESSAGE = "user_message"
    COMPLIANCE_WARNING = "compliance_warning"
    DATA_SYNC = "data_sync"


class NotificationPriority(Enum):
    """Notification priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryMethod(Enum):
    """Notification delivery methods."""
    IN_APP = "in_app"
    EMAIL = "email"
    WEBSOCKET = "websocket"
    PUSH = "push"


@dataclass
class Notification:
    """Notification data structure."""
    id: str
    user_id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    read: bool = False
    delivered: bool = False
    delivery_methods: List[DeliveryMethod] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "read": self.read,
            "delivered": self.delivered,
            "delivery_methods": [dm.value for dm in self.delivery_methods] if self.delivery_methods else []
        }


class NotificationService:
    """Real-time notification service."""
    
    def __init__(self):
        """Initialize notification service."""
        self.cache = None
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_subscriptions: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the notification service."""
        if self._initialized:
            return
        
        self.cache = get_cache()
        self._initialized = True
        logger.info("Notification service initialized")
    
    async def subscribe_user(self, user_id: str, notification_types: List[str],
                           delivery_methods: List[str]) -> Dict[str, Any]:
        """Subscribe user to specific notification types."""
        try:
            # Convert string types to enums
            types = []
            for nt in notification_types:
                try:
                    types.append(NotificationType(nt))
                except ValueError:
                    logger.warning(f"Invalid notification type: {nt}")
            
            methods = []
            for dm in delivery_methods:
                try:
                    methods.append(DeliveryMethod(dm))
                except ValueError:
                    logger.warning(f"Invalid delivery method: {dm}")
            
            # Store subscription
            subscription = {
                "user_id": user_id,
                "notification_types": [t.value for t in types],
                "delivery_methods": [m.value for m in methods],
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.user_subscriptions[user_id] = subscription
            
            # Cache subscription
            await self.cache.set(
                f"notification_subscription:{user_id}",
                subscription,
                ttl=86400  # 24 hours
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "subscribed_types": [t.value for t in types],
                "delivery_methods": [m.value for m in methods]
            }
            
        except Exception as e:
            logger.error(f"Failed to subscribe user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send notification to user through subscribed channels."""
        try:
            # Check if user is subscribed to this notification type
            subscription = await self._get_user_subscription(notification.user_id)
            if not subscription or not subscription.get("active"):
                return {"success": False, "reason": "user_not_subscribed"}
            
            subscribed_types = subscription.get("notification_types", [])
            if notification.type.value not in subscribed_types:
                return {"success": False, "reason": "notification_type_not_subscribed"}
            
            delivery_methods = subscription.get("delivery_methods", ["in_app"])
            delivery_results = {}
            
            # Store notification in cache
            await self.cache.set(
                f"notification:{notification.id}",
                notification.to_dict(),
                ttl=604800  # 7 days
            )
            
            # Add to user's notification list
            await self._add_to_user_notifications(notification.user_id, notification.id)
            
            # Deliver through each subscribed method
            for method in delivery_methods:
                try:
                    if method == "websocket":
                        result = await self._deliver_websocket(notification)
                        delivery_results["websocket"] = result
                    elif method == "in_app":
                        result = await self._deliver_in_app(notification)
                        delivery_results["in_app"] = result
                    elif method == "email":
                        result = await self._deliver_email(notification)
                        delivery_results["email"] = result
                    elif method == "push":
                        result = await self._deliver_push(notification)
                        delivery_results["push"] = result
                except Exception as e:
                    logger.error(f"Failed to deliver via {method}: {e}")
                    delivery_results[method] = {"success": False, "error": str(e)}
            
            # Mark as delivered if at least one method succeeded
            notification.delivered = any(r.get("success", False) for r in delivery_results.values())
            
            # Update notification status
            await self.cache.set(
                f"notification:{notification.id}",
                notification.to_dict(),
                ttl=604800
            )
            
            # Log delivery
            await log_business_event(
                "notification_sent",
                {
                    "notification_id": notification.id,
                    "user_id": notification.user_id,
                    "type": notification.type.value,
                    "priority": notification.priority.value,
                    "delivered": notification.delivered,
                    "delivery_results": delivery_results
                }
            )
            
            return {
                "success": True,
                "notification_id": notification.id,
                "delivered": notification.delivered,
                "delivery_results": delivery_results
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {"success": False, "error": str(e)}
    
    async def connect_websocket(self, websocket: WebSocket, user_id: str):
        """Connect user's WebSocket for real-time notifications."""
        try:
            await websocket.accept()
            
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            
            self.active_connections[user_id].add(websocket)
            logger.info(f"WebSocket connected for user {user_id}")
            
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send pending notifications
            await self._send_pending_notifications(websocket, user_id)
            
        except Exception as e:
            logger.error(f"WebSocket connection failed for user {user_id}: {e}")
    
    async def disconnect_websocket(self, websocket: WebSocket, user_id: str):
        """Disconnect user's WebSocket."""
        try:
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            logger.info(f"WebSocket disconnected for user {user_id}")
            
        except Exception as e:
            logger.error(f"WebSocket disconnection error for user {user_id}: {e}")
    
    async def get_user_notifications(self, user_id: str, limit: int = 50,
                                   unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get user's notifications."""
        try:
            # Get notification IDs for user
            notification_ids = await self.cache.get(f"user_notifications:{user_id}") or []
            
            # Limit results
            notification_ids = notification_ids[-limit:] if limit else notification_ids
            
            notifications = []
            for notification_id in reversed(notification_ids):  # Most recent first
                notification_data = await self.cache.get(f"notification:{notification_id}")
                if notification_data:
                    if unread_only and notification_data.get("read", False):
                        continue
                    notifications.append(notification_data)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read."""
        try:
            notification_data = await self.cache.get(f"notification:{notification_id}")
            if not notification_data:
                return False
            
            if notification_data.get("user_id") != user_id:
                return False  # User doesn't own this notification
            
            notification_data["read"] = True
            await self.cache.set(f"notification:{notification_id}", notification_data, ttl=604800)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification read: {e}")
            return False
    
    async def bulk_notify(self, notification_type: NotificationType, title: str,
                         message: str, data: Dict[str, Any], user_ids: List[str],
                         priority: NotificationPriority = NotificationPriority.MEDIUM) -> Dict[str, Any]:
        """Send notification to multiple users."""
        try:
            results = []
            
            for user_id in user_ids:
                notification = Notification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    type=notification_type,
                    priority=priority,
                    title=title,
                    message=message,
                    data=data,
                    created_at=datetime.now()
                )
                
                result = await self.send_notification(notification)
                results.append({
                    "user_id": user_id,
                    "notification_id": notification.id,
                    "success": result.get("success", False)
                })
            
            successful = sum(1 for r in results if r["success"])
            
            return {
                "success": True,
                "total_users": len(user_ids),
                "successful_deliveries": successful,
                "failed_deliveries": len(user_ids) - successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Bulk notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's notification subscription."""
        if user_id in self.user_subscriptions:
            return self.user_subscriptions[user_id]
        
        # Try cache
        subscription = await self.cache.get(f"notification_subscription:{user_id}")
        if subscription:
            self.user_subscriptions[user_id] = subscription
        
        return subscription
    
    async def _add_to_user_notifications(self, user_id: str, notification_id: str):
        """Add notification ID to user's notification list."""
        user_notifications = await self.cache.get(f"user_notifications:{user_id}") or []
        user_notifications.append(notification_id)
        
        # Keep only last 1000 notifications per user
        if len(user_notifications) > 1000:
            user_notifications = user_notifications[-1000:]
        
        await self.cache.set(f"user_notifications:{user_id}", user_notifications, ttl=2592000)  # 30 days
    
    async def _deliver_websocket(self, notification: Notification) -> Dict[str, Any]:
        """Deliver notification via WebSocket."""
        try:
            if notification.user_id not in self.active_connections:
                return {"success": False, "reason": "no_active_connections"}
            
            message = {
                "type": "notification",
                "notification": notification.to_dict()
            }
            
            connections = self.active_connections[notification.user_id].copy()
            delivered = False
            
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                    delivered = True
                except Exception as e:
                    logger.warning(f"Failed to send to WebSocket: {e}")
                    # Remove dead connection
                    self.active_connections[notification.user_id].discard(websocket)
            
            return {"success": delivered, "connections_attempted": len(connections)}
            
        except Exception as e:
            logger.error(f"WebSocket delivery failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deliver_in_app(self, notification: Notification) -> Dict[str, Any]:
        """Deliver notification via in-app storage."""
        # In-app notifications are stored in cache and retrieved when user requests them
        return {"success": True, "method": "in_app_storage"}
    
    async def _deliver_email(self, notification: Notification) -> Dict[str, Any]:
        """Deliver notification via email."""
        # Email delivery would integrate with email service (SendGrid, SES, etc.)
        # For now, just log the attempt
        logger.info(f"Email notification would be sent to user {notification.user_id}: {notification.title}")
        return {"success": True, "method": "email_placeholder"}
    
    async def _deliver_push(self, notification: Notification) -> Dict[str, Any]:
        """Deliver notification via push notification."""
        # Push notifications would integrate with FCM, APNs, etc.
        # For now, just log the attempt
        logger.info(f"Push notification would be sent to user {notification.user_id}: {notification.title}")
        return {"success": True, "method": "push_placeholder"}
    
    async def _send_pending_notifications(self, websocket: WebSocket, user_id: str):
        """Send pending unread notifications to newly connected WebSocket."""
        try:
            notifications = await self.get_user_notifications(user_id, limit=10, unread_only=True)
            
            for notification_data in notifications:
                await websocket.send_json({
                    "type": "pending_notification",
                    "notification": notification_data
                })
            
            if notifications:
                logger.info(f"Sent {len(notifications)} pending notifications to user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to send pending notifications: {e}")
    
    async def cleanup_expired_notifications(self):
        """Background task to clean up expired notifications."""
        try:
            # This would scan for expired notifications and remove them
            # Implementation depends on your specific requirements
            logger.info("Notification cleanup task executed")
            
        except Exception as e:
            logger.error(f"Notification cleanup failed: {e}")
    
    async def get_notification_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get notification statistics."""
        try:
            if user_id:
                # User-specific stats
                notifications = await self.get_user_notifications(user_id, limit=100)
                unread_count = sum(1 for n in notifications if not n.get("read", False))
                
                return {
                    "user_id": user_id,
                    "total_notifications": len(notifications),
                    "unread_notifications": unread_count,
                    "read_notifications": len(notifications) - unread_count,
                    "active_websocket_connections": len(self.active_connections.get(user_id, set()))
                }
            else:
                # Global stats
                return {
                    "total_active_connections": sum(len(conns) for conns in self.active_connections.values()),
                    "connected_users": len(self.active_connections),
                    "total_subscriptions": len(self.user_subscriptions)
                }
                
        except Exception as e:
            logger.error(f"Failed to get notification stats: {e}")
            return {"error": str(e)}


# Helper functions for common notification types

async def notify_tariff_update(user_id: str, hts_code: str, old_rate: float, 
                             new_rate: float, notification_service: NotificationService):
    """Send tariff update notification."""
    notification = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=NotificationType.TARIFF_UPDATE,
        priority=NotificationPriority.HIGH,
        title="Tariff Rate Updated",
        message=f"Tariff rate for HTS {hts_code} changed from {old_rate}% to {new_rate}%",
        data={
            "hts_code": hts_code,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "change_percent": ((new_rate - old_rate) / old_rate) * 100 if old_rate > 0 else 0
        },
        created_at=datetime.now()
    )
    
    return await notification_service.send_notification(notification)


async def notify_calculation_complete(user_id: str, job_id: str, total_calculations: int,
                                    successful: int, notification_service: NotificationService):
    """Send bulk calculation completion notification."""
    notification = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=NotificationType.CALCULATION_COMPLETE,
        priority=NotificationPriority.MEDIUM,
        title="Bulk Calculation Complete",
        message=f"Processed {successful}/{total_calculations} calculations successfully",
        data={
            "job_id": job_id,
            "total_calculations": total_calculations,
            "successful": successful,
            "failed": total_calculations - successful
        },
        created_at=datetime.now()
    )
    
    return await notification_service.send_notification(notification)


# Global notification service instance
notification_service = NotificationService() 