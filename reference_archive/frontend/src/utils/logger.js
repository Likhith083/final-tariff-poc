// Frontend Logging System
class Logger {
  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.logLevel = this.isDevelopment ? 'debug' : 'info';
    this.logLevels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3
    };
  }

  shouldLog(level) {
    return this.logLevels[level] <= this.logLevels[this.logLevel];
  }

  formatMessage(level, component, message, data = null) {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}] [${component}]`;
    
    if (data) {
      return `${prefix}: ${message}`, data;
    }
    return `${prefix}: ${message}`;
  }

  error(component, message, error = null) {
    if (this.shouldLog('error')) {
      console.error(this.formatMessage('error', component, message));
      if (error) {
        console.error('Error details:', error);
        if (error.stack) {
          console.error('Stack trace:', error.stack);
        }
      }
    }
  }

  warn(component, message, data = null) {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', component, message), data);
    }
  }

  info(component, message, data = null) {
    if (this.shouldLog('info')) {
      console.info(this.formatMessage('info', component, message), data);
    }
  }

  debug(component, message, data = null) {
    if (this.shouldLog('debug')) {
      console.log(this.formatMessage('debug', component, message), data);
    }
  }

  // API specific logging
  apiRequest(component, endpoint, method, data = null) {
    this.debug(component, `API Request: ${method} ${endpoint}`, data);
  }

  apiResponse(component, endpoint, status, data = null) {
    if (status >= 400) {
      this.error(component, `API Error: ${status} ${endpoint}`, data);
    } else {
      this.debug(component, `API Response: ${status} ${endpoint}`, data);
    }
  }

  // Component lifecycle logging
  componentMount(component, props = null) {
    this.debug(component, 'Component mounted', props);
  }

  componentUnmount(component) {
    this.debug(component, 'Component unmounted');
  }

  componentUpdate(component, prevProps, nextProps) {
    this.debug(component, 'Component updated', { prevProps, nextProps });
  }

  // State change logging
  stateChange(component, action, prevState, nextState) {
    this.debug(component, `State change: ${action}`, { prevState, nextState });
  }

  // User interaction logging
  userAction(component, action, data = null) {
    this.info(component, `User action: ${action}`, data);
  }
}

// Create singleton instance
const logger = new Logger();

// Export both the class and instance
export { Logger };
export default logger; 