"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, Star, Mail } from "lucide-react";

export function DcHero() {
  const [email, setEmail] = useState("");

  return (
    <section className="relative overflow-hidden bg-[#0a1628]">
      {/* Grid lines background */}
      <div
        className="absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
      />
      {/* Diagonal accent lines */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(45deg, rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(-45deg, rgba(255,255,255,0.3) 1px, transparent 1px)",
          backgroundSize: "120px 120px",
        }}
      />

      <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-20 lg:py-24">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-16">
          {/* LEFT — Headline + CTAs */}
          <div>
            <h1 className="text-4xl font-bold leading-[1.1] tracking-tight text-white sm:text-5xl lg:text-[3.5rem]">
              Learn to code.
              <br />
              Build real things.
            </h1>

            <p className="mt-4 max-w-lg text-base leading-relaxed text-white/70 sm:text-lg">
              Master in-demand skills in Python, JavaScript, React, and more
              through interactive courses, real-world projects, and industry-recognized
              certifications.
            </p>

            {/* CTA Buttons */}
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href="/sign-up"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#2dbe52] px-7 py-3.5 text-base font-bold text-white transition-colors hover:bg-[#25a848]"
              >
                Start Learning for Free
              </Link>
              <Link
                href="/projects"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-7 py-3.5 text-base font-bold text-[#0a1628] transition-colors hover:bg-white/90"
              >
                Explore Projects
              </Link>
            </div>

            {/* Rating */}
            <div className="mt-8 flex items-center gap-2">
              <div className="flex items-center gap-1">
                <span className="text-lg font-bold text-white">4.7</span>
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star
                      key={i}
                      className={`h-4 w-4 ${
                        i <= 4
                          ? "fill-[#f59e0b] text-[#f59e0b]"
                          : "fill-[#f59e0b]/40 text-[#f59e0b]/40"
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT — Sign Up Card */}
          <div className="flex justify-center lg:justify-end">
            <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
              <h2 className="text-center text-xl font-bold text-[#0a1628]">
                Create Your Free Account
              </h2>

              <div className="mt-5 space-y-3">
                {/* Google button */}
                <button className="flex w-full items-center justify-center gap-3 rounded-lg bg-[#2dbe52] px-4 py-3.5 text-base font-bold text-white transition-colors hover:bg-[#25a848]">
                  <svg className="h-5 w-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="currentColor"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  Continue with Google
                </button>

                {/* Show more options */}
                <button className="flex w-full items-center justify-center gap-1 text-sm font-medium text-[#4f46e5] hover:underline">
                  Show more options
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Divider */}
                <div className="flex items-center gap-3 py-1">
                  <div className="h-px flex-1 bg-gray-200" />
                  <span className="text-xs text-gray-400">or</span>
                  <div className="h-px flex-1 bg-gray-200" />
                </div>

                {/* Email input */}
                <div className="relative">
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-lg border-2 border-gray-300 px-4 py-3.5 text-sm text-[#0a1628] placeholder:text-gray-400 outline-none transition-colors focus:border-[#4f46e5]"
                  />
                  <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              {/* Terms */}
              <p className="mt-4 text-center text-xs text-gray-500">
                By continuing, you accept our{" "}
                <a href="#" className="text-[#4f46e5] underline">
                  Terms of Use
                </a>
                , our{" "}
                <a href="#" className="text-[#4f46e5] underline">
                  Privacy Policy
                </a>{" "}
                and that your data is stored in the USA.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
