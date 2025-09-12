import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ProtectedRoute, VerifiedRoute } from "@/components/ProtectedRoute";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import UserDashboard from "./pages/UserDashboard";
import ContributorDashboard from "./pages/ContributorDashboard";
import OrganizationDashboard from "./pages/OrganizationDashboard";
import DiasporaDashboard from "./pages/DiasporaDashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <ErrorBoundary>
    <ThemeProvider>
      <AuthProvider>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected Dashboard Routes - Require Authentication */}
                <Route
                  path="/dashboard/user"
                  element={
                    <ProtectedRoute>
                      <UserDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard/contributor"
                  element={
                    <ProtectedRoute>
                      <ContributorDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Fully Verified Routes - Require Authentication + KYC + Wallet */}
                <Route
                  path="/dashboard/organization"
                  element={
                    <VerifiedRoute>
                      <OrganizationDashboard />
                    </VerifiedRoute>
                  }
                />
                <Route
                  path="/dashboard/diaspora"
                  element={
                    <VerifiedRoute>
                      <DiasporaDashboard />
                    </VerifiedRoute>
                  }
                />

                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </QueryClientProvider>
      </AuthProvider>
    </ThemeProvider>
  </ErrorBoundary>
);

export default App;
