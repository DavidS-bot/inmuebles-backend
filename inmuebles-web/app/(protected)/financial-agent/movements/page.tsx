"use client";
import { useState } from "react";
import TabNavigation from "@/components/TabNavigation";
import MovementsTab from "@/components/MovementsTab";
import RulesTab from "@/components/RulesTab";

export default function FinancialMovementsPage() {
  const [activeTab, setActiveTab] = useState('movements');

  const tabs = [
    {
      id: 'movements',
      label: 'Movimientos',
      icon: '💰',
      content: <MovementsTab />
    },
    {
      id: 'rules',
      label: 'Reglas de Clasificación',
      icon: '⚙️',
      content: <RulesTab />
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">💰 Movimientos & Reglas</h1>
          <p className="text-gray-600 mt-1">Gestión de extractos bancarios y reglas de clasificación</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <TabNavigation 
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
    </div>
  );
}