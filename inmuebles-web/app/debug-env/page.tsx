"use client";

export default function DebugPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Environment Debug</h1>
      <div className="space-y-2">
        <p><strong>NEXT_PUBLIC_API_URL:</strong> {process.env.NEXT_PUBLIC_API_URL || "NOT SET"}</p>
        <p><strong>Current URL:</strong> {typeof window !== 'undefined' ? window.location.origin : "Server Side"}</p>
        <p><strong>User Agent:</strong> {typeof navigator !== 'undefined' ? navigator.userAgent : "Server Side"}</p>
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-2">Test API Connection</h2>
        <button 
          onClick={async () => {
            try {
              const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
              const data = await response.text();
              alert(`API Response: ${response.status} - ${data}`);
            } catch (error) {
              alert(`API Error: ${error}`);
            }
          }}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Test API Connection
        </button>
      </div>
      
      <div className="mt-4">
        <button 
          onClick={async () => {
            try {
              const formData = new URLSearchParams();
              formData.append('username', 'davsanchez21277@gmail.com');
              formData.append('password', '123456');
              
              const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
              });
              
              const data = await response.json();
              
              if (response.status === 200 && data.access_token) {
                // Simulate full login flow
                localStorage.setItem("auth_token", data.access_token);
                document.cookie = `t=${data.access_token}; Path=/; SameSite=Lax`;
                alert(`Login SUCCESS! Token saved. Redirecting to dashboard...`);
                window.location.href = "/dashboard";
              } else {
                alert(`Login Response: ${response.status} - ${JSON.stringify(data)}`);
              }
            } catch (error) {
              alert(`Login Error: ${error}`);
            }
          }}
          className="bg-green-500 text-white px-4 py-2 rounded ml-4"
        >
          Test Full Login Flow
        </button>
      </div>
      
      <div className="mt-4">
        <button 
          onClick={() => {
            const token = localStorage.getItem("auth_token");
            const cookie = document.cookie.split("; ").find(x=>x.startsWith("t="))?.split("=")[1];
            alert(`Stored Token: ${token ? token.substr(0,20) + "..." : "NONE"}\nCookie: ${cookie ? cookie.substr(0,20) + "..." : "NONE"}`);
          }}
          className="bg-purple-500 text-white px-4 py-2 rounded"
        >
          Check Stored Token
        </button>
        
        <button 
          onClick={() => {
            localStorage.removeItem("auth_token");
            document.cookie = "t=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
            alert("Token cleared!");
          }}
          className="bg-red-500 text-white px-4 py-2 rounded ml-4"
        >
          Clear Token
        </button>
      </div>
    </div>
  );
}