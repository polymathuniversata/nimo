import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/hooks/useAuth';
import { KycData } from '@/types/auth';
import {
  Mail,
  Lock,
  User,
  Wallet,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Loader2,
  MapPin,
  FileText,
  Calendar,
  Phone,
  Globe,
  CreditCard,
  Camera,
  Upload,
  Shield
} from 'lucide-react';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, submitKyc, isLoading } = useAuth();

  // Traditional registration state
  const [traditionalForm, setTraditionalForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    location: '',
    bio: '',
    skills: '',
  });

  // KYC state
  const [kycForm, setKycForm] = useState<KycData>({
    date_of_birth: '',
    nationality: '',
    phone_number: '',
    id_document_type: 'passport',
    id_document_number: '',
    id_document_front_url: '',
    id_document_back_url: '',
    selfie_url: '',
    address_street: '',
    address_city: '',
    address_state: '',
    address_country: '',
    address_postal_code: '',
    address_proof_url: '',
  });

  // Wallet registration state
  const [walletForm, setWalletForm] = useState({
    walletAddress: '',
    signature: '',
    message: '',
    name: '',
    location: '',
    bio: '',
    skills: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isWalletConnecting, setIsWalletConnecting] = useState(false);
  const [currentStep, setCurrentStep] = useState<'profile' | 'kyc' | 'wallet'>('profile');

  const handleTraditionalRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (traditionalForm.password !== traditionalForm.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (traditionalForm.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    try {
      const skills = traditionalForm.skills
        ? traditionalForm.skills.split(',').map(s => s.trim()).filter(s => s)
        : [];

      // First, register the user
      await register({
        email: traditionalForm.email,
        password: traditionalForm.password,
        name: traditionalForm.name,
        location: traditionalForm.location,
        bio: traditionalForm.bio,
        skills,
        authMethod: 'traditional',
      });

      // Then submit KYC if wallet is connected
      if (walletForm.walletAddress) {
        await submitKyc(kycForm);
      }

      setSuccess('Registration and KYC submission successful! You can now sign in.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
    }
  };

  const handleWalletRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Ensure wallet is connected
    if (!walletForm.walletAddress) {
      setError('Please connect your Cardano wallet first');
      return;
    }

    try {
      const skills = walletForm.skills
        ? walletForm.skills.split(',').map(s => s.trim()).filter(s => s)
        : [];

      // Register with wallet
      await register({
        walletAddress: walletForm.walletAddress,
        name: walletForm.name,
        location: walletForm.location,
        bio: walletForm.bio,
        skills,
        authMethod: 'wallet',
      });

      // Submit KYC
      await submitKyc(kycForm);

      setSuccess('Wallet registration and KYC submission successful! You can now sign in.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
    }
  };

  const handleFileUpload = async (file: File, type: keyof KycData) => {
    // In a real implementation, you would upload to IPFS or a secure storage
    // For now, we'll create a placeholder URL
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Placeholder for file upload - in production, upload to IPFS
      const mockUrl = `https://ipfs.nimo.network/${type}/${Date.now()}-${file.name}`;
      
      setKycForm(prev => ({
        ...prev,
        [type]: mockUrl
      }));
      
      setSuccess(`${type.replace('_', ' ')} uploaded successfully`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'File upload failed');
    }
  };

  const connectWallet = async () => {
    setIsWalletConnecting(true);
    setError('');

    try {
      // This is a placeholder for actual wallet connection
      // In a real implementation, you would integrate with Cardano wallet extensions
      if (window.cardano && window.cardano.yoroi) {
        const wallet = await window.cardano.yoroi.enable();
        const addresses = await wallet.getUsedAddresses();
        const walletAddress = addresses[0];

        // Generate a challenge message
        const message = `Sign this message to register with Nimo: ${Date.now()}`;
        const signature = await wallet.signData(walletAddress, Buffer.from(message).toString('hex'));

        setWalletForm(prev => ({
          ...prev,
          walletAddress,
          signature: signature.signature,
          message,
        }));

        setSuccess('Wallet connected successfully! Please complete your profile.');
      } else {
        throw new Error('Please install a Cardano wallet extension (Yoroi, Eternl, etc.)');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to connect wallet');
    } finally {
      setIsWalletConnecting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-primary">Nimo</h1>
          </div>
          <h2 className="text-2xl font-semibold text-foreground mb-2">Join Nimo</h2>
          <p className="text-muted-foreground">Create your decentralized identity and start earning reputation</p>
        </div>

        {/* Registration Form */}
        <Card className="shadow-lg border-0 bg-white/95 backdrop-blur-sm">
          <CardHeader className="space-y-1">
            <CardTitle className="text-xl text-center">Create Account</CardTitle>
            <CardDescription className="text-center">
              Complete your profile, KYC verification, and wallet connection
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Step Indicator */}
            <div className="flex items-center justify-center mb-6">
              <div className="flex items-center space-x-4">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep === 'profile' ? 'bg-primary text-white' : currentStep === 'kyc' || currentStep === 'wallet' ? 'bg-green-500 text-white' : 'bg-muted text-muted-foreground'}`}>
                  <User className="w-4 h-4" />
                </div>
                <div className={`w-12 h-0.5 ${currentStep === 'kyc' || currentStep === 'wallet' ? 'bg-green-500' : 'bg-muted'}`}></div>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep === 'kyc' ? 'bg-primary text-white' : currentStep === 'wallet' ? 'bg-green-500 text-white' : 'bg-muted text-muted-foreground'}`}>
                  <FileText className="w-4 h-4" />
                </div>
                <div className={`w-12 h-0.5 ${currentStep === 'wallet' ? 'bg-green-500' : 'bg-muted'}`}></div>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${currentStep === 'wallet' ? 'bg-primary text-white' : 'bg-muted text-muted-foreground'}`}>
                  <Wallet className="w-4 h-4" />
                </div>
              </div>
            </div>

            <Tabs value={currentStep} className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger 
                  value="profile" 
                  onClick={() => setCurrentStep('profile')}
                  disabled={currentStep === 'kyc' || currentStep === 'wallet'}
                  className="flex items-center space-x-2"
                >
                  <User className="w-4 h-4" />
                  <span>Profile</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="kyc" 
                  onClick={() => setCurrentStep('kyc')}
                  disabled={!walletForm.walletAddress}
                  className="flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>KYC</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="wallet" 
                  onClick={() => setCurrentStep('wallet')}
                  disabled={!walletForm.walletAddress}
                  className="flex items-center space-x-2"
                >
                  <Wallet className="w-4 h-4" />
                  <span>Wallet</span>
                </TabsTrigger>
              </TabsList>

              {/* Profile Step */}
              <TabsContent value="profile" className="space-y-4">
                <div className="text-center mb-4">
                  <h3 className="text-lg font-semibold">Create Your Profile</h3>
                  <p className="text-sm text-muted-foreground">Start by setting up your basic information</p>
                </div>

                <form onSubmit={(e) => { e.preventDefault(); setCurrentStep('kyc'); }} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name *</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="name"
                          placeholder="Your full name"
                          value={traditionalForm.name}
                          onChange={(e) => setTraditionalForm(prev => ({ ...prev, name: e.target.value }))}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email *</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="your@email.com"
                          value={traditionalForm.email}
                          onChange={(e) => setTraditionalForm(prev => ({ ...prev, email: e.target.value }))}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="location">Location (Optional)</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="location"
                        placeholder="City, Country"
                        value={traditionalForm.location}
                        onChange={(e) => setTraditionalForm(prev => ({ ...prev, location: e.target.value }))}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="password">Password *</Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="password"
                          type="password"
                          placeholder="Min 6 characters"
                          value={traditionalForm.password}
                          onChange={(e) => setTraditionalForm(prev => ({ ...prev, password: e.target.value }))}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm Password *</Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="confirmPassword"
                          type="password"
                          placeholder="Confirm password"
                          value={traditionalForm.confirmPassword}
                          onChange={(e) => setTraditionalForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="bio">Bio (Optional)</Label>
                    <Textarea
                      id="bio"
                      placeholder="Tell us about yourself..."
                      value={traditionalForm.bio}
                      onChange={(e) => setTraditionalForm(prev => ({ ...prev, bio: e.target.value }))}
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="skills">Skills (Optional)</Label>
                    <div className="relative">
                      <FileText className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="skills"
                        placeholder="Python, React, Design (comma-separated)"
                        value={traditionalForm.skills}
                        onChange={(e) => setTraditionalForm(prev => ({ ...prev, skills: e.target.value }))}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <Button type="submit" className="w-full">
                    Next: KYC Verification
                  </Button>
                </form>
              </TabsContent>

              {/* KYC Step */}
              <TabsContent value="kyc" className="space-y-4">
                <div className="text-center mb-4">
                  <h3 className="text-lg font-semibold">KYC Verification</h3>
                  <p className="text-sm text-muted-foreground">Complete your identity verification</p>
                </div>

                <div className="space-y-6">
                  {/* Personal Information */}
                  <div className="space-y-4">
                    <h4 className="font-medium flex items-center">
                      <User className="w-4 h-4 mr-2" />
                      Personal Information
                    </h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="dateOfBirth">Date of Birth *</Label>
                        <div className="relative">
                          <Calendar className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="dateOfBirth"
                            type="date"
                            value={kycForm.date_of_birth}
                            onChange={(e) => setKycForm(prev => ({ ...prev, date_of_birth: e.target.value }))}
                            className="pl-10"
                            required
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="nationality">Nationality *</Label>
                        <div className="relative">
                          <Globe className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="nationality"
                            placeholder="Your nationality"
                            value={kycForm.nationality}
                            onChange={(e) => setKycForm(prev => ({ ...prev, nationality: e.target.value }))}
                            className="pl-10"
                            required
                          />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="phoneNumber">Phone Number *</Label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="phoneNumber"
                          placeholder="+1234567890"
                          value={kycForm.phone_number}
                          onChange={(e) => setKycForm(prev => ({ ...prev, phone_number: e.target.value }))}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Document Information */}
                  <div className="space-y-4">
                    <h4 className="font-medium flex items-center">
                      <CreditCard className="w-4 h-4 mr-2" />
                      Identity Document
                    </h4>

                    <div className="space-y-2">
                      <Label htmlFor="documentType">Document Type *</Label>
                      <Select value={kycForm.id_document_type} onValueChange={(value: 'passport' | 'national_id' | 'drivers_license') => setKycForm(prev => ({ ...prev, id_document_type: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select document type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="passport">Passport</SelectItem>
                          <SelectItem value="national_id">National ID</SelectItem>
                          <SelectItem value="drivers_license">Driver's License</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="documentNumber">Document Number *</Label>
                      <Input
                        id="documentNumber"
                        placeholder="Enter document number"
                        value={kycForm.id_document_number}
                        onChange={(e) => setKycForm(prev => ({ ...prev, id_document_number: e.target.value }))}
                        required
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Document Front *</Label>
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 text-center">
                          <Camera className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                          <p className="text-sm text-muted-foreground mb-2">Upload front of document</p>
                          <Input
                            type="file"
                            accept="image/*"
                            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0], 'id_document_front_url')}
                            className="hidden"
                            id="documentFront"
                          />
                          <Label htmlFor="documentFront" className="cursor-pointer">
                            <Button variant="outline" size="sm" asChild>
                              <span><Upload className="w-4 h-4 mr-2" />Upload</span>
                            </Button>
                          </Label>
                          {kycForm.id_document_front_url && (
                            <p className="text-xs text-green-600 mt-2">✓ Uploaded</p>
                          )}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Document Back (Optional)</Label>
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 text-center">
                          <Camera className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                          <p className="text-sm text-muted-foreground mb-2">Upload back of document</p>
                          <Input
                            type="file"
                            accept="image/*"
                            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0], 'id_document_back_url')}
                            className="hidden"
                            id="documentBack"
                          />
                          <Label htmlFor="documentBack" className="cursor-pointer">
                            <Button variant="outline" size="sm" asChild>
                              <span><Upload className="w-4 h-4 mr-2" />Upload</span>
                            </Button>
                          </Label>
                          {kycForm.id_document_back_url && (
                            <p className="text-xs text-green-600 mt-2">✓ Uploaded</p>
                          )}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Selfie *</Label>
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 text-center">
                          <Camera className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                          <p className="text-sm text-muted-foreground mb-2">Upload selfie</p>
                          <Input
                            type="file"
                            accept="image/*"
                            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0], 'selfie_url')}
                            className="hidden"
                            id="selfie"
                          />
                          <Label htmlFor="selfie" className="cursor-pointer">
                            <Button variant="outline" size="sm" asChild>
                              <span><Upload className="w-4 h-4 mr-2" />Upload</span>
                            </Button>
                          </Label>
                          {kycForm.selfie_url && (
                            <p className="text-xs text-green-600 mt-2">✓ Uploaded</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Address Information */}
                  <div className="space-y-4">
                    <h4 className="font-medium flex items-center">
                      <MapPin className="w-4 h-4 mr-2" />
                      Address Information
                    </h4>

                    <div className="space-y-2">
                      <Label htmlFor="streetAddress">Street Address *</Label>
                      <Input
                        id="streetAddress"
                        placeholder="123 Main Street"
                        value={kycForm.address_street}
                        onChange={(e) => setKycForm(prev => ({ ...prev, address_street: e.target.value }))}
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="city">City *</Label>
                        <Input
                          id="city"
                          placeholder="City"
                          value={kycForm.address_city}
                          onChange={(e) => setKycForm(prev => ({ ...prev, address_city: e.target.value }))}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="state">State/Province (Optional)</Label>
                        <Input
                          id="state"
                          placeholder="State or Province"
                          value={kycForm.address_state}
                          onChange={(e) => setKycForm(prev => ({ ...prev, address_state: e.target.value }))}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="country">Country *</Label>
                        <Input
                          id="country"
                          placeholder="Country"
                          value={kycForm.address_country}
                          onChange={(e) => setKycForm(prev => ({ ...prev, address_country: e.target.value }))}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="postalCode">Postal Code *</Label>
                        <Input
                          id="postalCode"
                          placeholder="12345"
                          value={kycForm.address_postal_code}
                          onChange={(e) => setKycForm(prev => ({ ...prev, address_postal_code: e.target.value }))}
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Address Proof (Optional)</Label>
                      <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 text-center">
                        <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground mb-2">Upload utility bill or bank statement</p>
                        <Input
                          type="file"
                          accept="image/*,.pdf"
                          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0], 'address_proof_url')}
                          className="hidden"
                          id="addressProof"
                        />
                        <Label htmlFor="addressProof" className="cursor-pointer">
                          <Button variant="outline" size="sm" asChild>
                            <span><Upload className="w-4 h-4 mr-2" />Upload</span>
                          </Button>
                        </Label>
                        {kycForm.address_proof_url && (
                          <p className="text-xs text-green-600 mt-2">✓ Uploaded</p>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-4">
                    <Button variant="outline" onClick={() => setCurrentStep('profile')} className="flex-1">
                      Back
                    </Button>
                    <Button onClick={() => setCurrentStep('wallet')} className="flex-1">
                      Next: Connect Wallet
                    </Button>
                  </div>
                </div>
              </TabsContent>
              {/* Wallet Step */}
              <TabsContent value="wallet" className="space-y-4">
                <div className="text-center mb-4">
                  <h3 className="text-lg font-semibold">Connect Your Wallet</h3>
                  <p className="text-sm text-muted-foreground">Link your Cardano wallet to complete registration</p>
                </div>

                <div className="space-y-4">
                  {!walletForm.walletAddress ? (
                    <div className="p-6 border-2 border-dashed border-muted-foreground/25 rounded-lg text-center">
                      <Wallet className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <h4 className="font-medium mb-2">Wallet Connection Required</h4>
                      <p className="text-sm text-muted-foreground mb-4">
                        You need to connect your Cardano wallet to complete your registration and access the platform.
                      </p>
                      <Button
                        onClick={connectWallet}
                        disabled={isWalletConnecting}
                        className="w-full"
                      >
                        {isWalletConnecting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Connecting...
                          </>
                        ) : (
                          <>
                            <Wallet className="mr-2 h-4 w-4" />
                            Connect Cardano Wallet
                          </>
                        )}
                      </Button>
                      <p className="text-xs text-muted-foreground mt-2">
                        Supported wallets: Yoroi, Eternl, Nami, Flint
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          <span className="text-sm font-medium text-green-800">Wallet Connected Successfully</span>
                        </div>
                        <p className="text-xs text-green-700 font-mono">
                          {walletForm.walletAddress.slice(0, 8)}...{walletForm.walletAddress.slice(-8)}
                        </p>
                      </div>

                      <Alert>
                        <Shield className="h-4 w-4" />
                        <AlertDescription>
                          Your wallet will be used for secure authentication and to receive reputation tokens for your contributions.
                        </AlertDescription>
                      </Alert>

                      <div className="flex space-x-4">
                        <Button variant="outline" onClick={() => setCurrentStep('kyc')} className="flex-1">
                          Back
                        </Button>
                        <Button onClick={handleTraditionalRegister} disabled={isLoading} className="flex-1">
                          {isLoading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Creating Account...
                            </>
                          ) : (
                            'Complete Registration'
                          )}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>

            {/* Error/Success Messages */}
            {error && (
              <Alert className="mt-4 border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="mt-4 border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}

            {/* Footer */}
            <div className="mt-6 text-center space-y-2">
              <p className="text-sm text-muted-foreground">
                Already have an account?{' '}
                <Link to="/login" className="text-primary hover:underline font-medium">
                  Sign in here
                </Link>
              </p>
              <div className="flex items-center justify-center space-x-4 text-xs text-muted-foreground">
                <Badge variant="secondary" className="text-xs">
                  🔐 Secure Registration
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  🛡️ KYC Required
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  🌍 Decentralized Identity
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;