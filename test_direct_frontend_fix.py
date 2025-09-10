#!/usr/bin/env python3

import requests
import json

def test_direct_frontend_fix():
    """Test and create a direct fix for the frontend issue"""
    
    print("TESTING DIRECT FRONTEND FIX")
    print("=" * 50)
    
    # 1. Test the exact API call the frontend makes
    print("1. Testing exact frontend API flow...")
    
    # Login exactly as frontend does
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    try:
        # Step 1: Login
        response = requests.post(
            "https://inmuebles-backend-api.onrender.com/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        user_id = token_data.get("user_id")
        
        print(f"✅ Login successful")
        print(f"   Token: {token[:30]}...")
        print(f"   User ID: {user_id}")
        
        # Step 2: Test viability endpoint exactly as frontend
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://inmuebles-web.vercel.app",
            "Referer": "https://inmuebles-web.vercel.app/estudios-viabilidad"
        }
        
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers=headers
        )
        
        print(f"\n2. Viability API Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            studies = response.json()
            print(f"   Studies found: {len(studies)}")
            
            if len(studies) > 0:
                print(f"\n✅ STUDIES ARE WORKING!")
                print(f"   The API is returning {len(studies)} studies correctly")
                
                # Show what frontend should display
                total = len(studies)
                favorable = len([s for s in studies if s.get('net_annual_return', 0) > 0])
                avg_return = sum([s.get('net_annual_return', 0) for s in studies]) / len(studies)
                
                print(f"\n📊 FRONTEND SHOULD SHOW:")
                print(f"   Total Estudios: {total}")
                print(f"   Favorables: {favorable}")
                print(f"   Rentabilidad Media: {avg_return:.1%}")
                
                for i, study in enumerate(studies, 1):
                    name = study.get('study_name', 'N/A')
                    price = study.get('purchase_price', 0)
                    monthly_rent = study.get('monthly_rent', 0)
                    net_return = study.get('net_annual_return', 0)
                    risk = study.get('risk_level', 'N/A')
                    
                    print(f"   {i}. {name}")
                    print(f"      Price: EUR{price:,.0f} | Rent: EUR{monthly_rent:,.0f}")
                    print(f"      Return: {net_return:.2%} | Risk: {risk}")
                
                return True
            else:
                print(f"❌ No studies found!")
                return False
        else:
            print(f"❌ Viability API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_emergency_test_page():
    """Create a simple test page to verify the API is working"""
    
    print("\n" + "="*50)
    print("CREATING EMERGENCY TEST PAGE")
    print("="*50)
    
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Test Viability API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        .study { border: 1px solid #ccc; margin: 10px 0; padding: 10px; }
    </style>
</head>
<body>
    <h1>Test Viability API</h1>
    <button onclick="testAPI()">Test API</button>
    <div id="results"></div>

    <script>
        async function testAPI() {
            const results = document.getElementById('results');
            results.innerHTML = 'Testing...';
            
            try {
                // Login
                const loginData = new URLSearchParams();
                loginData.append('username', 'davsanchez21277@gmail.com');
                loginData.append('password', '123456');
                
                const loginResponse = await fetch('https://inmuebles-backend-api.onrender.com/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: loginData
                });
                
                if (!loginResponse.ok) {
                    throw new Error('Login failed: ' + loginResponse.status);
                }
                
                const tokenData = await loginResponse.json();
                const token = tokenData.access_token;
                
                results.innerHTML += '<div class="success">✅ Login successful</div>';
                
                // Get studies
                const studiesResponse = await fetch('https://inmuebles-backend-api.onrender.com/viability/', {
                    headers: {
                        'Authorization': 'Bearer ' + token,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!studiesResponse.ok) {
                    throw new Error('Studies failed: ' + studiesResponse.status);
                }
                
                const studies = await studiesResponse.json();
                
                results.innerHTML += '<div class="success">✅ Found ' + studies.length + ' studies</div>';
                
                // Display studies
                studies.forEach((study, i) => {
                    const studyDiv = document.createElement('div');
                    studyDiv.className = 'study';
                    studyDiv.innerHTML = `
                        <h3>${study.study_name}</h3>
                        <p>Price: €${study.purchase_price?.toLocaleString()}</p>
                        <p>Rent: €${study.monthly_rent?.toLocaleString()}/month</p>
                        <p>Return: ${(study.net_annual_return * 100)?.toFixed(2)}%</p>
                        <p>Risk: ${study.risk_level}</p>
                    `;
                    results.appendChild(studyDiv);
                });
                
            } catch (error) {
                results.innerHTML += '<div class="error">❌ Error: ' + error.message + '</div>';
            }
        }
    </script>
</body>
</html>'''
    
    try:
        with open("test_viability_api.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✅ Created test_viability_api.html")
        print("   Open this file in your browser to test the API directly")
        return True
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return False

if __name__ == "__main__":
    api_working = test_direct_frontend_fix()
    
    if api_working:
        print(f"\n🎉 THE API IS WORKING CORRECTLY!")
        print(f"   The problem is in the frontend, not the backend")
        print(f"   The frontend is not making the API calls properly")
        
        create_emergency_test_page()
        
        print(f"\n🔧 FRONTEND TROUBLESHOOTING STEPS:")
        print(f"   1. Clear ALL browser data (cookies, localStorage, cache)")
        print(f"   2. Use incognito/private browsing mode")
        print(f"   3. Check browser console for JavaScript errors")
        print(f"   4. Manually go to /login and login again")
        print(f"   5. Check if you're being redirected incorrectly")
        
    else:
        print(f"\n❌ API IS NOT WORKING")
        print(f"   Need to fix backend issues first")