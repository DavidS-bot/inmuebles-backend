"use client";
import { useState } from "react";

export default function TestLoginPage() {
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const testLogin = async () => {
    setLoading(true);
    setResult("Testing...");
    
    try {
      // Check API URL
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      console.log("API URL:", apiUrl);
      setResult(prev => prev + `\nAPI URL: ${apiUrl}`);

      // Test health endpoint first
      const healthResponse = await fetch(`${apiUrl}/health`);
      const healthData = await healthResponse.json();
      console.log("Health check:", healthData);
      setResult(prev => prev + `\nHealth: ${JSON.stringify(healthData)}`);

      // Test login
      const formData = new URLSearchParams();
      formData.append('username', 'davsanchez21277@gmail.com');
      formData.append('password', '123456');

      const loginResponse = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });

      if (!loginResponse.ok) {
        throw new Error(`HTTP ${loginResponse.status}: ${loginResponse.statusText}`);
      }

      const loginData = await loginResponse.json();
      console.log("Login result:", loginData);
      setResult(prev => prev + `\nLogin: ${loginData.access_token ? 'SUCCESS' : 'FAILED'}`);
      setResult(prev => prev + `\nToken: ${loginData.access_token?.substring(0, 20)}...`);

    } catch (error: any) {
      console.error("Error:", error);
      setResult(prev => prev + `\nError: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-4">Login Test Page</h1>
        
        <button 
          onClick={testLogin}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? "Testing..." : "Test Login"}
        </button>

        <div className="mt-4 bg-gray-50 p-4 rounded">
          <h3 className="font-semibold mb-2">Results:</h3>
          <pre className="whitespace-pre-wrap text-sm">{result}</pre>
        </div>
      </div>
    </div>
  );
}