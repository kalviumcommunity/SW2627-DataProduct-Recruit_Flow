'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Mail, Lock } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center p-4">
      <div className="w-full max-w-[420px] rounded-[10px] border border-[#27272A] bg-[#18181B] p-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">Recruitflow</h1>
          <p className="text-[13px] text-[#A1A1AA]">Welcome back. Please enter your details.</p>
        </div>

        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); router.push('/dashboard'); }}>
          {/* Email */}
          <div>
            <label className="block text-[13px] font-medium text-[#D4D4D8] mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full pl-9 pr-4 py-2.5 rounded-md border border-[#27272A] bg-[#09090B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-[13px] font-medium text-[#D4D4D8] mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-4 py-2.5 rounded-md border border-[#27272A] bg-[#09090B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]"
              />
            </div>
          </div>

          {/* Options */}
          <div className="flex items-center justify-between pt-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-3.5 h-3.5 rounded-sm border-[#3F3F46] bg-[#09090B] accent-[#C7D2FE]" />
              <span className="text-[12px] text-[#D4D4D8]">Keep me logged in</span>
            </label>
            <Link href="#" className="text-[12px] text-[#D4D4D8] hover:text-white transition-colors">
              Forgot password?
            </Link>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-2.5 mt-2 rounded-md bg-[#C7D2FE] text-[#0F172A] text-[13px] font-semibold hover:bg-[#B1BDED] transition-colors"
          >
            Sign In
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-[#27272A]"></div>
          </div>
          <div className="relative flex justify-center text-[10px] font-medium text-[#71717A] tracking-wider">
            <span className="px-2 bg-[#18181B] uppercase">Or continue with</span>
          </div>
        </div>

        {/* Social Buttons */}
        <div className="space-y-3">
          <button className="w-full flex items-center justify-center gap-2.5 py-2.5 rounded-md border border-[#27272A] bg-[#18181B] hover:bg-[#27272A] transition-colors text-[13px] font-medium text-[#D4D4D8]">
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </button>
          
          <button className="w-full flex items-center justify-center gap-2.5 py-2.5 rounded-md border border-[#27272A] bg-[#18181B] hover:bg-[#27272A] transition-colors text-[13px] font-medium text-[#D4D4D8]">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
            </svg>
            Sign in with SSO
          </button>
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-[12px] text-[#A1A1AA]">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-[#D4D4D8] hover:text-white transition-colors">
              Sign Up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
