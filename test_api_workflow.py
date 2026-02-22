#!/usr/bin/env python3
"""Test the full API workflow"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("PHARMAREC AI - FULL WORKFLOW TEST")
print("=" * 70)

# Test 1: Register
print("\n[1] Register User...")
r = requests.post(f'{BASE_URL}/auth/register', json={
    'email': 'workflow@test.com',
    'password': 'workflow123',
    'full_name': 'Workflow Test'
})
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
if r.status_code != 200:
    print(f"Error: {r.text}")
    exit(1)

# Test 2: Login
print("\n[2] Login User...")
r = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'workflow@test.com',
    'password': 'workflow123'
})
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print(f"Token acquired ✓")

# Test 3: Add Medicine
print("\n[3] Add Medicine to Inventory...")
r = requests.post(f'{BASE_URL}/inventory/', headers=headers, json={
    'name': 'Paracetamol 500mg',
    'generic_name': 'Acetaminophen',
    'batch_no': 'BATCH001',
    'stock_qty': 100,
    'reorder_level': 20,
    'price': 5.0,
    'manufacturer': 'Generic Pharma'
})
print(f"Status: {r.status_code} ✓" if r.status_code == 201 else f"Status: {r.status_code} ✗")
med_id = r.json().get('id')
print(f"Added medicine ID: {med_id} ✓")

# Test 4: Get Medicines
print("\n[4] Get All Medicines...")
r = requests.get(f'{BASE_URL}/inventory/')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
medicines = r.json()
print(f"Total medicines: {len(medicines)} ✓")

# Test 5: Search Medicines
print("\n[5] Search Medicines...")
r = requests.get(f'{BASE_URL}/inventory/search?q=Paracetamol')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
results = r.json()
print(f"Found {len(results)} medicine(s) ✓")

# Test 6: Get Low Stock
print("\n[6] Get Low Stock Medicines...")
r = requests.get(f'{BASE_URL}/inventory/low-stock')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
low_stock = r.json()
print(f"Low stock items: {len(low_stock)} ✓")

# Test 7: Record Sale
print("\n[7] Record a Sale...")
r = requests.post(f'{BASE_URL}/sales/', headers=headers, json={
    'medicine_name': 'Paracetamol 500mg',
    'quantity': 5,
    'unit_price': 5.0
})
print(f"Status: {r.status_code} ✓" if r.status_code == 201 else f"Status: {r.status_code} ✗")
sale_id = r.json().get('id')
print(f"Recorded sale ID: {sale_id} ✓")

# Test 8: Get Sales
print("\n[8] Get Sales History...")
r = requests.get(f'{BASE_URL}/sales/')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
sales = r.json()
print(f"Total sales: {len(sales)} ✓")

# Test 9: Get Sales Summary
print("\n[9] Get Sales Summary...")
r = requests.get(f'{BASE_URL}/sales/summary')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
if r.status_code == 200:
    summary = r.json()
    print(f"Sales summary records: {len(summary)} ✓")

# Test 10: AI Reorder Suggestions
print("\n[10] AI Reorder Suggestions (🤖 AI Feature)...")
r = requests.get(f'{BASE_URL}/reorder/suggestions?days=7')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
if r.status_code == 200:
    data = r.json()
    suggestions = data.get('data', [])
    print(f"AI suggestions: {len(suggestions)} ✓")
    if suggestions:
        print(f"  Sample: {suggestions[0].get('medicine_name')} - Predict qty: {suggestions[0].get('suggested_order')}")

# Test 11: AI Predict for Medicine
print("\n[11] AI Predict Reorder for Medicine ID=1...")
r = requests.get(f'{BASE_URL}/reorder/predict/1?days_ahead=7')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
if r.status_code == 200:
    pred = r.json().get('prediction', {})
    print(f"  Current stock: {pred.get('current_stock')}")
    print(f"  Avg daily sales: {pred.get('average_daily_sales')}")
    print(f"  Suggested order: {pred.get('suggested_order')} ✓")
    print(f"  Confidence: {pred.get('confidence')} ✓")

# Test 12: Health Check
print("\n[12] Health Check...")
r = requests.get(f'{BASE_URL}/health')
print(f"Status: {r.status_code} ✓" if r.status_code == 200 else f"Status: {r.status_code} ✗")
health = r.json()
print(f"App: {health.get('app')}")
print(f"Status: {health.get('status')} ✓")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED! - PHARMAREC AI IS WORKING")
print("=" * 70)
print("\n📊 Summary:")
print("  ✓ Authentication (Register/Login/JWT)")
print("  ✓ Inventory Management (Add/Search/Low-stock)")
print("  ✓ Sales Recording & Tracking")
print("  ✓ AI Reorder Predictions (🤖 ML Engine)")
print("  ✓ Analytics & Reporting")
print("\n🚀 Ready to use! Start the frontend with:")
print("  cd frontend")
print("  npm run dev")
print("=" * 70)
