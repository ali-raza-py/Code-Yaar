import type { Metadata } from "next";
import { Fraunces, Figtree, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/hooks/use-theme";
import { AuthProvider } from "@/hooks/use-auth";
import { MotionProvider } from "@/components/motion/reduced-motion";

// Display serif — a characterful variable face (SOFT/WONK axes unlocked) used
// for headings, hero type and the brand wordmark. Its academic warmth deliberately
// echoes the printed certificate so the product and its credentials feel related.
const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  axes: ["SOFT", "WONK"],
  display: "swap",
});

// Body / UI sans — clean, friendly and highly readable at small sizes; carries
// every control, label and paragraph so the serif stays reserved for emphasis.
const figtree = Figtree({
  variable: "--font-figtree",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Code-Yaar — Think. Build. Evolve.",
    template: "%s | Code-Yaar",
  },
  description:
    "A platform for becoming better at actually building software. Learn concepts, build projects, prove your skills.",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
    apple: "/favicon.svg",
  },
  openGraph: {
    title: "Code-Yaar — Think. Build. Evolve.",
    description:
      "A platform for becoming better at actually building software.",
    type: "website",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${figtree.variable} ${jetbrainsMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <ThemeProvider>
          <AuthProvider>
            <MotionProvider>
              {children}
            </MotionProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
