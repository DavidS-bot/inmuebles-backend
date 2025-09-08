interface PriorityTask {
  id: string;
  title: string;
  description: string;
  urgency: 'high' | 'medium' | 'low';
  icon: string;
  action: string;
  href: string;
}

interface PriorityTaskCardProps {
  task: PriorityTask;
}

export function PriorityTaskCard({ task }: PriorityTaskCardProps) {
  const getUrgencyColor = (urgency: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'border-l-red-500 bg-red-50';
      case 'medium': return 'border-l-yellow-500 bg-yellow-50';
      case 'low': return 'border-l-green-500 bg-green-50';
    }
  };

  const getUrgencyBadge = (urgency: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const getButtonColor = (urgency: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'bg-red-600 text-white hover:bg-red-700';
      case 'medium': return 'bg-yellow-600 text-white hover:bg-yellow-700';
      case 'low': return 'bg-green-600 text-white hover:bg-green-700';
    }
  };

  return (
    <div className={`border-l-4 rounded-xl p-6 ${getUrgencyColor(task.urgency)} transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl" role="img" aria-label={task.title}>
          {task.icon}
        </span>
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getUrgencyBadge(task.urgency)}`}>
          {task.urgency === 'high' ? 'Urgente' : task.urgency === 'medium' ? 'Medio' : 'Bajo'}
        </span>
      </div>
      
      <h3 className="font-semibold text-gray-900 mb-2">
        {task.title}
      </h3>
      
      <p className="text-sm text-gray-600 mb-4">
        {task.description}
      </p>
      
      <a 
        href={task.href}
        className={`inline-block px-4 py-2 rounded-lg font-medium text-sm transition-colors ${getButtonColor(task.urgency)}`}
      >
        {task.action}
      </a>
    </div>
  );
}