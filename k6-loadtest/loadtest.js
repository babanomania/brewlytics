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

// Generate a simple random string
function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyz';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

export function setup() {
  const apiUrl = __ENV.API_URL || 'http://localhost:8000';
  const headers = { 'Content-Type': 'application/json' };

  const customerIds = [];
  for (let i = 0; i < 10; i++) {
    const payload = {
      name: `User_${randomString(5)}`,
      email: `${randomString(5)}@example.com`,
    };
    const res = http.post(`${apiUrl}/customers`, JSON.stringify(payload), { headers });
    if (res.status === 200) {
      customerIds.push(res.json('id'));
    }
  }

  const productIds = [];
  for (let i = 0; i < 10; i++) {
    const payload = {
      name: `Prod_${randomString(5)}`,
      price: Math.floor(Math.random() * 10) + 1,
    };
    const res = http.post(`${apiUrl}/products`, JSON.stringify(payload), { headers });
    if (res.status === 200) {
      productIds.push(res.json('id'));
    }
  }

  return { customerIds, productIds };
}

export default function (data) {
  const apiUrl = __ENV.API_URL || 'http://localhost:8000';
  const headers = { 'Content-Type': 'application/json' };

  const customerId = data.customerIds[Math.floor(Math.random() * data.customerIds.length)];
  const numItems = Math.floor(Math.random() * 3) + 1; // 1-3 items
  const items = [];
  for (let i = 0; i < numItems; i++) {
    const productId = data.productIds[Math.floor(Math.random() * data.productIds.length)];
    const quantity = Math.floor(Math.random() * 5) + 1; // 1-5 quantity
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
