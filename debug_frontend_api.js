// Simple test to check if frontend can reach backend
console.log("Testing frontend API connection...");

// Check environment variables
console.log("API URL from env:", process.env.NEXT_PUBLIC_API_URL);

// Test fetch directly
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => {
    console.log("Backend health check:", data);
    
    // Now test login
    const formData = new URLSearchParams();
    formData.append('username', 'davsanchez21277@gmail.com');
    formData.append('password', '123456');
    
    return fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });
  })
  .then(response => response.json())
  .then(data => {
    console.log("Login test result:", data);
    if (data.access_token) {
      console.log("✅ Login works from JavaScript");
    } else {
      console.log("❌ Login failed from JavaScript");
    }
  })
  .catch(error => {
    console.error("❌ Network error:", error);
  });