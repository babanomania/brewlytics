import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '10s', target: 0 },
  ],
};

export default function () {
  const url = 'http://order-api:8000/orders';
  const payload = JSON.stringify({
    customer_id: 1,
    items: [{ product_id: 1, quantity: 1 }],
  });
  const params = { headers: { 'Content-Type': 'application/json' } };
  http.post(url, payload, params);
  sleep(1);
}
