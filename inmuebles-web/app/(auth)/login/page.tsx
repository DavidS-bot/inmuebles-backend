"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { persistToken } from "@/lib/auth";

export default function LoginPage() {
  const r = useRouter();
  const [email, setEmail] = useState("davsanchez21277@gmail.com");
  const [password, setPassword] = useState("123456");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      console.log("API URL:", process.env.NEXT_PUBLIC_API_URL);
      console.log("Sending login request:", { email, password: "***" });
      console.log("FormData:", Object.fromEntries(formData));
      
      const res = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });
      console.log("Login response:", res.data);
      const token = res.data?.access_token;
      if (!token) throw new Error("Token no recibido");
      persistToken(token);
      
      // Check if user is new (has no properties)
      try {
        const propertiesRes = await api.get("/properties", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (propertiesRes.data.length === 0) {
          r.push("/onboarding");
        } else {
          r.push("/financial-agent");
        }
      } catch (err) {
        // If properties check fails, go to onboarding
        r.push("/onboarding");
      }
    } catch (err: any) {
      console.error("Login error:", err);
      console.error("Error response:", err?.response?.data);
      setError(err?.response?.data?.detail ?? err?.message ?? "Error de login");
    } finally { setLoading(false); }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await api.post("/auth/register", { email, password });
      setIsRegister(false);
      setError("");
      alert("Usuario registrado exitosamente. Ahora puedes iniciar sesión.");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Error de registro");
    } finally { setLoading(false); }
  }

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Background with gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900" />
      
      {/* Property background image */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'url(/platon30.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          filter: 'contrast(1.2) brightness(1.1)'
        }}
      />
      
      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent" />
      
      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-2">
            Inmuebles Manager
          </h1>
          <p className="text-gray-400 text-lg">Sistema de Gestión de Propiedades</p>
        </div>
        
        {/* Login Form */}
        <form 
          onSubmit={isRegister ? handleRegister : handleLogin} 
          className="bg-white/10 backdrop-blur-xl p-8 rounded-2xl shadow-2xl max-w-md w-full space-y-6 border border-white/20"
        >
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-white mb-1">
              {isRegister ? "Crear Cuenta" : "Iniciar Sesión"}
            </h2>
            <p className="text-gray-400 text-sm">
              {isRegister ? "Únete a la plataforma" : "Accede a tu panel de control"}
            </p>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Correo Electrónico
              </label>
              <input 
                className="w-full px-4 py-3 bg-white/10 backdrop-blur border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" 
                value={email} 
                onChange={e=>setEmail(e.target.value)} 
                placeholder="tu@email.com" 
                type="email"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Contraseña
              </label>
              <input 
                className="w-full px-4 py-3 bg-white/10 backdrop-blur border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" 
                type="password" 
                value={password} 
                onChange={e=>setPassword(e.target.value)} 
                placeholder="••••••••" 
                required
              />
            </div>
          </div>
          
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <button 
            disabled={loading} 
            className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {isRegister ? "Registrando..." : "Iniciando..."}
              </span>
            ) : (isRegister ? "Registrarse" : "Acceder")}
          </button>
          
          <div className="text-center space-y-3">
            <button 
              type="button" 
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
                setEmail(isRegister ? "davsanchez21277@gmail.com" : "");
                setPassword(isRegister ? "123456" : "");
              }}
              className="text-gray-400 hover:text-white text-sm transition-colors"
            >
              {isRegister ? "¿Ya tienes cuenta? Iniciar sesión" : "¿No tienes cuenta? Registrarse"}
            </button>
            
            <div className="pt-4 border-t border-white/10">
              <p className="text-xs text-gray-500">
                Made in Chaparrito with ❤️
              </p>
            </div>
          </div>
        </form>
        
        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-gray-500 text-sm">
            © 2024 Inmuebles Manager. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </main>
  );
}