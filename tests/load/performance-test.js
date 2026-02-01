"""
K6 Performance Testing Script for BarberX
Professional-grade load testing with realistic user scenarios.
"""

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const loginRate = new Rate('successful_logins');
const uploadRate = new Rate('successful_uploads');
const apiResponseTime = new Trend('api_response_time');
const tierUpgradeCounter = new Counter('tier_upgrades');

// Test configuration
export const options = {
  stages: [
    // Ramp-up: 0 to 100 users over 2 minutes
    { duration: '2m', target: 100 },
    
    // Stay at 100 users for 5 minutes
    { duration: '5m', target: 100 },
    
    // Ramp-up: 100 to 300 users over 3 minutes (peak load)
    { duration: '3m', target: 300 },
    
    // Stay at 300 users for 3 minutes (stress test)
    { duration: '3m', target: 300 },
    
    // Ramp-down: 300 to 0 users over 2 minutes
    { duration: '2m', target: 0 },
  ],
  
  thresholds: {
    // HTTP errors should be less than 1%
    http_req_failed: ['rate<0.01'],
    
    // 95% of requests should be below 500ms
    http_req_duration: ['p(95)<500'],
    
    // API calls should be below 200ms for 90% of requests
    api_response_time: ['p(90)<200'],
    
    // Login success rate should be above 95%
    successful_logins: ['rate>0.95'],
  },
};

// Base URL
const BASE_URL = 'http://localhost:5000';

// Test data
const tiers = ['FREE', 'STARTER', 'PROFESSIONAL', 'PREMIUM', 'ENTERPRISE'];
const testUsers = generateTestUsers();

function generateTestUsers() {
  const users = [];
  
  // Generate 100 test users across different tiers
  for (let i = 0; i < 100; i++) {
    const tier = tiers[Math.floor(Math.random() * tiers.length)];
    users.push({
      email: `testuser${i}@barberx.com`,
      password: 'TestPass123!',
      tier: tier,
    });
  }
  
  return users;
}

// Main test scenario
export default function() {
  // Select random user
  const user = testUsers[Math.floor(Math.random() * testUsers.length)];
  
  group('User Authentication', function() {
    // Login
    const loginPayload = JSON.stringify({
      email: user.email,
      password: user.password,
    });
    
    const loginParams = {
      headers: { 'Content-Type': 'application/json' },
    };
    
    const loginRes = http.post(`${BASE_URL}/auth/login`, loginPayload, loginParams);
    
    loginRate.add(loginRes.status === 200);
    
    check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'login response time < 200ms': (r) => r.timings.duration < 200,
    });
    
    sleep(1);
  });
  
  group('Dashboard & Usage', function() {
    // View dashboard
    const dashboardRes = http.get(`${BASE_URL}/dashboard`);
    
    check(dashboardRes, {
      'dashboard loaded': (r) => r.status === 200,
      'dashboard response time < 300ms': (r) => r.timings.duration < 300,
    });
    
    // Check usage statistics
    const usageRes = http.get(`${BASE_URL}/api/usage/current`);
    apiResponseTime.add(usageRes.timings.duration);
    
    check(usageRes, {
      'usage API response is 200': (r) => r.status === 200,
      'usage API response time < 100ms': (r) => r.timings.duration < 100,
    });
    
    sleep(2);
  });
  
  if (user.tier !== 'FREE') {
    group('File Upload (Paid Tiers)', function() {
      // Simulate video upload
      const uploadPayload = JSON.stringify({
        filename: 'bwc_video_test.mp4',
        size_mb: 256,
        duration_minutes: 15,
      });
      
      const uploadParams = {
        headers: { 'Content-Type': 'application/json' },
      };
      
      const uploadRes = http.post(`${BASE_URL}/api/upload/video`, uploadPayload, uploadParams);
      
      uploadRate.add(uploadRes.status === 200 || uploadRes.status === 201);
      
      check(uploadRes, {
        'upload initiated': (r) => r.status === 200 || r.status === 201,
        'upload response time < 500ms': (r) => r.timings.duration < 500,
      });
      
      sleep(3);
    });
  }
  
  if (user.tier === 'PROFESSIONAL' || user.tier === 'PREMIUM' || user.tier === 'ENTERPRISE') {
    group('Advanced Features (PRO+)', function() {
      // Legal research query
      const searchPayload = JSON.stringify({
        query: 'Fourth Amendment',
        jurisdiction: 'federal',
      });
      
      const searchParams = {
        headers: { 'Content-Type': 'application/json' },
      };
      
      const searchRes = http.post(`${BASE_URL}/api/legal-library/search`, searchPayload, searchParams);
      apiResponseTime.add(searchRes.timings.duration);
      
      check(searchRes, {
        'search completed': (r) => r.status === 200,
        'search response time < 300ms': (r) => r.timings.duration < 300,
      });
      
      // Generate timeline
      const timelineRes = http.post(`${BASE_URL}/api/timeline/generate`, JSON.stringify({
        case_id: Math.floor(Math.random() * 100),
      }), searchParams);
      
      check(timelineRes, {
        'timeline generated': (r) => r.status === 200 || r.status === 202,
      });
      
      sleep(2);
    });
  }
  
  if (user.tier === 'PREMIUM' || user.tier === 'ENTERPRISE') {
    group('API Access (PREMIUM+)', function() {
      // API key header
      const apiParams = {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'pk_test_' + user.email.split('@')[0],
        },
      };
      
      // Forensic analysis API
      const forensicPayload = JSON.stringify({
        case_id: Math.floor(Math.random() * 500),
        analysis_type: 'voice_stress',
      });
      
      const forensicRes = http.post(`${BASE_URL}/api/v1/forensic/analyze`, forensicPayload, apiParams);
      apiResponseTime.add(forensicRes.timings.duration);
      
      check(forensicRes, {
        'forensic API accessible': (r) => r.status === 200 || r.status === 202,
        'forensic API response time < 200ms': (r) => r.timings.duration < 200,
      });
      
      sleep(1);
    });
  }
  
  group('Health & Monitoring', function() {
    // Health check endpoint
    const healthRes = http.get(`${BASE_URL}/health`);
    
    check(healthRes, {
      'health check passed': (r) => r.status === 200,
      'health check response time < 50ms': (r) => r.timings.duration < 50,
    });
  });
  
  sleep(Math.random() * 3 + 1); // Random sleep 1-4 seconds
}

// Spike test scenario (optional)
export function spike() {
  group('Spike Test - Rapid Requests', function() {
    for (let i = 0; i < 10; i++) {
      const healthRes = http.get(`${BASE_URL}/health`);
      check(healthRes, {
        'spike test - health check OK': (r) => r.status === 200,
      });
    }
  });
}

// Soak test scenario (optional)
export function soak() {
  // Long-running test to detect memory leaks
  const user = testUsers[0];
  
  const loginPayload = JSON.stringify({
    email: user.email,
    password: user.password,
  });
  
  const loginRes = http.post(`${BASE_URL}/auth/login`, loginPayload, {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(loginRes, {
    'soak test - login OK': (r) => r.status === 200,
  });
  
  sleep(5);
}

// Teardown - runs once at the end
export function teardown(data) {
  console.log('');
  console.log('='.repeat(60));
  console.log('Performance Test Summary');
  console.log('='.repeat(60));
  console.log('Test completed successfully!');
  console.log('Review metrics above for detailed results.');
  console.log('='.repeat(60));
}
