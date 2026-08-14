import './globals.css';

export const metadata = {
  title: 'Recruitflow — Talent Command',
  description: 'Recruitment analytics dashboard. Command your talent pipeline, identify leaks, and optimize hiring.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0A0E1A] text-[#F0F4F8] antialiased">{children}</body>
    </html>
  );
}
