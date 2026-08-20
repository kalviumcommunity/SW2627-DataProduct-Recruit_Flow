'use client';

import { useState } from 'react';
import Link from 'next/link';
import { User, Mail, Building, Lock, EyeOff, Eye } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    companyName: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          full_name: formData.fullName,
          password: formData.password
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Signup failed');
      }

      // Success, redirect to login
      router.push('/login');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#121212] flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-center px-16 xl:px-24">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-12">
          <div className="grid grid-cols-2 gap-[2px]">
            <div className="w-2.5 h-2.5 bg-[#A1A1AA] rounded-sm"></div>
            <div className="w-2.5 h-2.5 bg-[#A1A1AA] rounded-sm"></div>
            <div className="w-2.5 h-2.5 bg-[#A1A1AA] rounded-sm"></div>
            <div className="w-2.5 h-2.5 bg-[#A1A1AA] rounded-sm"></div>
          </div>
          <span className="text-xl font-bold text-white tracking-tight">Recruitflow</span>
        </div>

        {/* Heading */}
        <h1 className="text-[40px] leading-[1.1] font-bold text-white mb-6">
          Command Your<br />
          <span className="text-[#D4D4D8]">Talent Pipeline</span>
        </h1>

        {/* Subtitle */}
        <p className="text-[#A1A1AA] text-[15px] leading-relaxed max-w-md mb-12">
          Start identifying leaks in your recruitment funnel today. A systematic approach to high-velocity talent acquisition.
        </p>

        {/* Trust Badges */}
        <div className="flex items-center gap-4">
          <div className="flex -space-x-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="w-8 h-8 rounded-full border-2 border-[#121212] bg-[#27272A] flex items-center justify-center overflow-hidden">
                <div className="w-full h-full bg-[#3F3F46] opacity-50" />
              </div>
            ))}
          </div>
          <div>
            <div className="flex gap-[2px] mb-1">
              {[...Array(5)].map((_, i) => (
                <svg key={i} className="w-[14px] h-[14px] text-[#22C55E]" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <div className="text-[10px] font-bold text-[#A1A1AA] uppercase tracking-wider">
              Trusted by top teams
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-[420px] rounded-[10px] border border-[#27272A] bg-[#18181B] p-8">
          
          <div className="mb-8">
            <h2 className="text-xl font-bold text-white mb-2">Create Account</h2>
            <p className="text-[13px] text-[#A1A1AA]">Set up your workspace and invite your team.</p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-md bg-red-900/50 border border-red-500 text-red-200 text-xs">
              {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-[13px] font-medium text-[#D4D4D8] mb-2">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
                <input 
                  type="text" 
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                  placeholder="Jane Doe" 
                  className="w-full pl-9 pr-4 py-2.5 rounded-md border border-[#27272A] bg-[#09090B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]" 
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-[13px] font-medium text-[#D4D4D8] mb-2">Work Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
                <input 
                  type="email" 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="jane@company.com" 
                  className="w-full pl-9 pr-4 py-2.5 rounded-md border border-[#27272A] bg-[#09090B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]" 
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-[13px] font-medium text-[#D4D4D8] mb-2">Company Name</label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
                <input 
                  type="text" 
                  value={formData.companyName}
                  onChange={(e) => setFormData({...formData, companyName: e.target.value})}
                  placeholder="Acme Corp" 
                  className="w-full pl-9 pr-4 py-2.5 rounded-md border border-[#27272A] bg-[#09090B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]" 
                />
              </div>
            </div>

            <div>
              <label className="block text-[13px] font-medium text-[#D4D4D8] mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
                <input 
                  type={showPassword ? 'text' : 'password'} 
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="••••••••" 
                  className="w-full pl-9 pr-10 py-2.5 rounded-md border border-[#27272A] bg-[#09090B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]" 
                  required
                  minLength={8}
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#71717A]">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-start gap-2.5 pt-2">
              <input type="checkbox" required className="w-3.5 h-3.5 mt-0.5 rounded-sm border-[#3F3F46] bg-[#09090B] accent-[#1E293B]" />
              <label className="text-[12px] text-[#A1A1AA] leading-tight">
                I agree to the <span className="text-[#D4D4D8] underline decoration-[#71717A] underline-offset-2">Terms of Service</span> and <span className="text-[#D4D4D8] underline decoration-[#71717A] underline-offset-2">Privacy Policy</span>.
              </label>
            </div>

            <button disabled={isLoading} type="submit" className="w-full flex items-center justify-center gap-2 py-2.5 mt-2 rounded-md bg-[#1E293B] hover:bg-[#334155] text-white text-[13px] font-semibold transition-colors disabled:opacity-50">
              {isLoading ? 'Creating Account...' : 'Create Account'}
              {!isLoading && <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>}
            </button>
          </form>

          <div className="text-center mt-6 pt-6 border-t border-[#27272A]">
            <p className="text-[12px] text-[#A1A1AA]">
              Already have an account? <Link href="/login" className="text-white hover:underline decoration-[#A1A1AA] underline-offset-2">Log In</Link>
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
