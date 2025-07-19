import http from 'k6/http';
import { sleep, check } from 'k6';

// Load test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 }, // ramp to 10 VUs
    { duration: '2m', target: 30 }, // hold at 30 VUs
    { duration: '2m', target: 50 }, // spike to 50 VUs
    { duration: '30s', target: 0 }, // ramp down
  ],
};

function getRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const productBaseNames = [
  'Espresso',
  'Latte',
  'Cappuccino',
  'Flat White',
  'Mocha',
  'Cold Brew',
  'Chai Latte',
  'Americano',
  'Cortado',
  'Macchiato',
];

const productSizes = ['Small', 'Medium', 'Large'];

function generateProduct() {
  const size = getRandom(productSizes);
  const base = getRandom(productBaseNames);
  const price = +(Math.random() * 5 + 2).toFixed(2); // 2-7 range
  return { name: `${size} ${base}`, price };
}

const firstNames = [
  'Alice',
  'Bob',
  'Priya',
  'John',
  'Maria',
  'Wei',
  'Ahmed',
  'Olivia',
  'Carlos',
  'Nina',
];

const lastNames = [
  'Smith',
  'Patel',
  'Garcia',
  'Jones',
  'Khan',
  'Kim',
  'Chen',
  'Brown',
  'Singh',
  'Davis',
];

function generateCustomer() {
  const first = getRandom(firstNames);
  const last = getRandom(lastNames);
  return {
    name: `${first} ${last}`,
    email: `${first.toLowerCase()}.${last.toLowerCase()}@example.com`,
  };
}

export function setup() {
  const apiUrl = __ENV.API_URL || 'http://localhost:8000';
  const headers = { 'Content-Type': 'application/json' };

  const customerIds = [];
  const usedEmails = new Set();
  while (customerIds.length < 10) {
    const payload = generateCustomer();
    if (usedEmails.has(payload.email)) {
      continue;
    }
    const res = http.post(`${apiUrl}/customers`, JSON.stringify(payload), { headers });
    if (res.status === 200) {
      customerIds.push(res.json('id'));
      usedEmails.add(payload.email);
    }
  }

  const productIds = [];
  const usedProductNames = new Set();
  while (productIds.length < 10) {
    const payload = generateProduct();
    if (usedProductNames.has(payload.name)) {
      continue;
    }
    const res = http.post(`${apiUrl}/products`, JSON.stringify(payload), { headers });
    if (res.status === 200) {
      productIds.push(res.json('id'));
      usedProductNames.add(payload.name);
    }
  }

  return { customerIds, productIds };
}

export default function (data) {
  const apiUrl = __ENV.API_URL || 'http://localhost:8000';
  const headers = { 'Content-Type': 'application/json' };

  if (Math.random() < 0.05) {
    const res = http.post(`${apiUrl}/customers`, JSON.stringify(generateCustomer()), { headers });
    if (res.status === 200) {
      data.customerIds.push(res.json('id'));
    }
  }

  if (Math.random() < 0.05) {
    const res = http.post(`${apiUrl}/products`, JSON.stringify(generateProduct()), { headers });
    if (res.status === 200) {
      data.productIds.push(res.json('id'));
    }
  }

  const customerId = data.customerIds[randomInt(0, data.customerIds.length - 1)];
  const numItems = randomInt(1, 3); // 1-3 items
  const items = [];
  for (let i = 0; i < numItems; i++) {
    const productId = data.productIds[randomInt(0, data.productIds.length - 1)];
    const quantity = randomInt(1, 5); // 1-5 quantity
    items.push({ product_id: productId, quantity });
  }

  const payload = JSON.stringify({ customer_id: customerId, items });
  const res = http.post(`${apiUrl}/orders`, payload, { headers });

  const success = check(res, {
    'status is 200': (r) => r.status === 200,
    'has order_id': (r) => !!r.json('order_id'),
  });

  if (!success || res.timings.duration > 500) {
    console.error(`Request failed or slow: status ${res.status}, duration ${res.timings.duration}ms`);
  }

  sleep(1);
}
