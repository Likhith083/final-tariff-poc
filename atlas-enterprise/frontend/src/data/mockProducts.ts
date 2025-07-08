export interface Product {
  id: string;
  name: string;
  description: string;
  htsCode: string;
  alternatives: Array<{
    id: string;
    name: string;
    htsCode: string;
    reason: string;
  }>;
  tags?: string[];
}

export const mockProducts: Product[] = [
  {
    id: 'prod-1',
    name: 'Laptop Computer',
    description: 'Standard 15-inch business laptop, Intel i7, 16GB RAM, 512GB SSD',
    htsCode: '8471.30.0100',
    tags: ['electronics', 'computers'],
    alternatives: [
      {
        id: 'alt-1',
        name: 'Chromebook',
        htsCode: '8471.41.0100',
        reason: 'Lower cost, suitable for web-based tasks'
      },
      {
        id: 'alt-2',
        name: 'Tablet with Keyboard',
        htsCode: '8471.60.0100',
        reason: 'Portable, touch interface, good for travel'
      }
    ]
  },
  {
    id: 'prod-2',
    name: 'Smartphone',
    description: '5G smartphone, 128GB storage, dual SIM',
    htsCode: '8517.12.0050',
    tags: ['electronics', 'phones'],
    alternatives: [
      {
        id: 'alt-3',
        name: 'Feature Phone',
        htsCode: '8517.12.0020',
        reason: 'Lower cost, basic calling and texting'
      },
      {
        id: 'alt-4',
        name: 'Satellite Phone',
        htsCode: '8525.60.1010',
        reason: 'Works in remote areas, emergency use'
      }
    ]
  }
]; 