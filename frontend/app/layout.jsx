import './globals.css';

export const metadata = {
  title: 'HR Recruitment Intelligence',
  description: 'Recruitment analytics dashboard and upload workflow.'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}
