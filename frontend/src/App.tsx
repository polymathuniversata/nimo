import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { TokenProvider } from "@/contexts/TokenContext";
import { ContributionsProvider } from "@/contexts/ContributionsContext";
import { WalletProvider } from "@/contexts/WalletContext";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ProtectedRoute } from "@/components/ProtectedRoute";
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
        <TokenProvider>
          <ContributionsProvider>
            <WalletProvider>
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
                      <Route
                        path="/dashboard/organization"
                        element={
                          <ProtectedRoute>
                            <OrganizationDashboard />
                          </ProtectedRoute>
                        }
                      />
                      <Route
                        path="/dashboard/diaspora"
                        element={
                          <ProtectedRoute>
                            <DiasporaDashboard />
                          </ProtectedRoute>
                        }
                      />

                      {/* 404 Route */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </BrowserRouter>
                </TooltipProvider>
              </QueryClientProvider>
            </WalletProvider>
          </ContributionsProvider>
        </TokenProvider>
      </AuthProvider>
    </ThemeProvider>
  </ErrorBoundary>
);

export default App;
