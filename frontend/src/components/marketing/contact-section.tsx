"use client";

import { Reveal } from "@/components/motion/reveal";
import { Mail, ArrowUpRight } from "lucide-react";

export function ContactSection() {
  return (
    <section id="contact" className="border-b bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <Reveal variant="fade-up">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
              Contact
            </div>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Get in touch
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted-foreground">
              Have questions about Code-Yaar? Want to collaborate or learn more?
              We&apos;d love to hear from you.
            </p>
          </Reveal>

          <Reveal variant="fade-up" delay={0.15}>
            <div className="mt-8">
              <a
                href="mailto:hello@code-yaar.dev"
                className="group inline-flex items-center gap-3 rounded-lg border border-border/50 bg-surface-recessed/50 px-6 py-4 transition-colors hover:border-primary/30 hover:shadow-sm"
              >
                <Mail className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">hello@code-yaar.dev</span>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
              </a>
            </div>
          </Reveal>

          <Reveal variant="fade-in" delay={0.3}>
            <p className="mt-6 text-xs text-muted-foreground/50">
              We respond to all messages. Feedback helps us build better.
            </p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
