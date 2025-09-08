"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import OnboardingWizard from "@/components/OnboardingWizard";

export default function OnboardingPage() {
  const router = useRouter();
  const [debugMode, setDebugMode] = useState(false);

  const handleOnboardingComplete = () => {
    // Redirect to main dashboard after successful onboarding
    router.push('/financial-agent');
  };

  // Debug view to test if page loads
  if (debugMode) {
    return (
      <div className="min-h-screen bg-blue-50 p-8">
        <div className="max-w-md mx-auto bg-white rounded-lg p-6">
          <h1 className="text-2xl font-bold mb-4">🚀 Onboarding Debug Mode</h1>
          <p className="mb-4">La página está cargando correctamente!</p>
          <button 
            onClick={() => setDebugMode(false)}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Continuar al Onboarding Real
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Debug toggle for testing */}
      <button 
        onClick={() => setDebugMode(true)}
        className="fixed top-4 right-4 z-50 bg-red-500 text-white px-2 py-1 text-xs rounded"
        style={{ display: process.env.NODE_ENV === 'development' ? 'block' : 'none' }}
      >
        Debug
      </button>
      
      <OnboardingWizard onComplete={handleOnboardingComplete} />
    </div>
  );
}