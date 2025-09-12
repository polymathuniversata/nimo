/// <reference types="vite/client" />

// Cardano Wallet API Type Definitions
interface CardanoPaginate {
  page: number;
  limit: number;
}

interface CardanoWalletAPI {
  enable(): Promise<CardanoWallet>;
  isEnabled(): Promise<boolean>;
  getUsedAddresses(): Promise<string[]>;
  getUnusedAddresses(): Promise<string[]>;
  getChangeAddress(): Promise<string>;
  getRewardAddresses(): Promise<string[]>;
  signData(address: string, payload: string): Promise<{ signature: string; key: string }>;
  signTx(tx: string, partialSign: boolean): Promise<string>;
  submitTx(tx: string): Promise<string>;
  getBalance(): Promise<string>;
  getUtxos(amount?: string, paginate?: CardanoPaginate): Promise<string[]>;
  getCollateral(): Promise<string[]>;
  experimental?: {
    getCollateral(): Promise<string[]>;
  };
  apiVersion?: string;
}

interface CardanoWallet {
  enable(): Promise<CardanoWallet>;
  isEnabled(): Promise<boolean>;
  getUsedAddresses(): Promise<string[]>;
  getUnusedAddresses(): Promise<string[]>;
  getChangeAddress(): Promise<string>;
  getRewardAddresses(): Promise<string[]>;
  signData(address: string, payload: string): Promise<{ signature: string; key: string }>;
  signTx(tx: string, partialSign: boolean): Promise<string>;
  submitTx(tx: string): Promise<string>;
  getBalance(): Promise<string>;
  getUtxos(amount?: string, paginate?: CardanoPaginate): Promise<string[]>;
  getCollateral(): Promise<string[]>;
  experimental?: {
    getCollateral(): Promise<string[]>;
  };
}

interface CardanoWallets {
  yoroi?: CardanoWalletAPI;
  eternl?: CardanoWalletAPI;
  nami?: CardanoWalletAPI;
  flint?: CardanoWalletAPI;
  gerowallet?: CardanoWalletAPI;
  lace?: CardanoWalletAPI;
  typhon?: CardanoWalletAPI;
  vespr?: CardanoWalletAPI;
  [key: string]: CardanoWalletAPI | undefined;
}

declare global {
  interface Window {
    cardano?: CardanoWallets;
  }
}
