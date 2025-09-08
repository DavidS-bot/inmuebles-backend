import ResponsiveLayout from '@/components/ResponsiveLayout';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ResponsiveLayout>
      {children}
    </ResponsiveLayout>
  );
}