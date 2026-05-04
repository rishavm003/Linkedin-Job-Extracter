import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "@/providers/Providers";
import Sidebar from "@/components/layout/Sidebar";
import TopBar from "@/components/layout/TopBar";
import MobileNav from "@/components/layout/MobileNav";
import { TooltipProvider } from "@/components/ui/tooltip";
import ClientGate from "@/components/layout/ClientGate";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "JobExtractor — Fresher Jobs Dashboard",
  description: "Find entry-level and fresher jobs across India and remote",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        <Providers>
          <TooltipProvider>
            <ClientGate>
              <div id="__next" className="flex h-full"> 
                {/* Sidebar - Desktop only */}
                <Sidebar />
                
                {/* Main content area */}
                <div className="flex-1 md:ml-60">
                  {/* Top navigation */}
                  <TopBar />
                  
                  {/* Page content */}
                  <main className="flex-1 p-6 pb-20 md:pb-6">
                    {children}
                  </main>
                </div>
              </div>
              
              {/* Mobile navigation */}
              <MobileNav />
            </ClientGate>
          </TooltipProvider>
        </Providers>
      </body>
    </html>
  );
}
