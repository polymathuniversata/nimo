import React from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Wallet,
  Coins,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Eye,
  EyeOff,
  ArrowUpRight,
  ArrowDownLeft,
  MoreHorizontal
} from 'lucide-react'
import { useTokens } from '@/contexts/TokenContext'
import { useWallet } from '@/contexts/WalletContext'

interface TokenBalanceProps {
  showDetailedView?: boolean
  showTransactions?: boolean
  maxTransactions?: number
  onViewAll?: () => void
  onRefresh?: () => void
}

export function TokenBalance({
  showDetailedView = false,
  showTransactions = true,
  maxTransactions = 5,
  onViewAll,
  onRefresh
}: TokenBalanceProps) {
  const { state: tokenState, refreshData } = useTokens()
  const { state: walletState } = useWallet()
  const [showBalances, setShowBalances] = React.useState(true)

  const handleRefresh = async () => {
    if (onRefresh) {
      onRefresh()
    } else {
      await refreshData()
    }
  }

  const formatCurrency = (amount: number, currency: string = 'ADA') => {
    return `${amount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })} ${currency}`
  }

  const formatTokenAmount = (amount: number) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(2)}M`
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(2)}K`
    }
    return amount.toString()
  }

  // Mock portfolio performance data
  const portfolioChange = 12.5 // +12.5% this month
  const isPositiveChange = portfolioChange >= 0

  return (
    <div className="space-y-6">
      {/* Balance Overview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Wallet className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Token Balance</h3>
              <p className="text-sm text-muted-foreground">
                {walletState.wallet?.walletName || 'Wallet'} • {walletState.wallet?.network || 'Preview'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowBalances(!showBalances)}
            >
              {showBalances ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={tokenState.loading}
            >
              <RefreshCw className={`w-4 h-4 ${tokenState.loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {/* Total Balance */}
        <div className="text-center mb-6">
          <div className="text-3xl font-bold mb-2">
            {showBalances ? (
              <span className="text-foreground">
                {formatCurrency(tokenState.balance.adaBalance + (tokenState.balance.nimoTokens * 0.001), 'ADA')}
              </span>
            ) : (
              <span className="text-muted-foreground">••••••</span>
            )}
          </div>
          <div className="flex items-center justify-center gap-2 text-sm">
            {isPositiveChange ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500" />
            )}
            <span className={isPositiveChange ? 'text-green-600' : 'text-red-600'}>
              {isPositiveChange ? '+' : ''}{portfolioChange}% this month
            </span>
          </div>
        </div>

        {/* Token Breakdown */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-4 bg-muted/30 rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Coins className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium">NIMO Tokens</span>
            </div>
            <div className="text-xl font-semibold mb-1">
              {showBalances ? (
                formatTokenAmount(tokenState.balance.nimoTokens)
              ) : (
                '••••'
              )}
            </div>
            <div className="text-xs text-muted-foreground">
              Available: {showBalances ? formatTokenAmount(tokenState.balance.availableTokens) : '••••'}
            </div>
          </div>

          <div className="text-center p-4 bg-muted/30 rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Wallet className="w-5 h-5 text-secondary" />
              <span className="text-sm font-medium">ADA Balance</span>
            </div>
            <div className="text-xl font-semibold mb-1">
              {showBalances ? (
                formatCurrency(tokenState.balance.adaBalance, 'ADA')
              ) : (
                '•••••• ADA'
              )}
            </div>
            <div className="text-xs text-muted-foreground">
              Staked: {showBalances ? formatTokenAmount(tokenState.balance.stakedTokens) : '••••'}
            </div>
          </div>
        </div>

        {/* Staking Progress */}
        {tokenState.balance.stakedTokens > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Staking Progress</span>
              <span className="text-sm text-muted-foreground">
                {Math.round((tokenState.balance.stakedTokens / tokenState.balance.nimoTokens) * 100)}% staked
              </span>
            </div>
            <Progress
              value={(tokenState.balance.stakedTokens / tokenState.balance.nimoTokens) * 100}
              className="h-2"
            />
          </div>
        )}
      </Card>

      {/* Recent Transactions */}
      {showTransactions && tokenState.transactions.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg">Recent Transactions</h3>
            {onViewAll && (
              <Button variant="ghost" size="sm" onClick={onViewAll}>
                <MoreHorizontal className="w-4 h-4 mr-2" />
                View All
              </Button>
            )}
          </div>

          <div className="space-y-3">
            {tokenState.transactions.slice(0, maxTransactions).map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${
                    transaction.type === 'reward'
                      ? 'bg-green-100 text-green-600'
                      : transaction.type === 'transfer'
                        ? 'bg-blue-100 text-blue-600'
                        : transaction.type === 'stake'
                          ? 'bg-purple-100 text-purple-600'
                          : 'bg-gray-100 text-gray-600'
                  }`}>
                    {transaction.type === 'reward' && <ArrowDownLeft className="w-4 h-4" />}
                    {transaction.type === 'transfer' && <ArrowUpRight className="w-4 h-4" />}
                    {transaction.type === 'stake' && <TrendingUp className="w-4 h-4" />}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{transaction.description}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(transaction.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className={`font-semibold ${
                    transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.amount > 0 ? '+' : ''}{formatTokenAmount(Math.abs(transaction.amount))}
                  </p>
                  <Badge variant="outline" className="text-xs">
                    {transaction.type}
                  </Badge>
                </div>
              </div>
            ))}
          </div>

          {tokenState.transactions.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Wallet className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No transactions yet</p>
              <p className="text-sm">Start contributing to earn rewards!</p>
            </div>
          )}
        </Card>
      )}

      {/* Quick Actions */}
      {showDetailedView && (
        <Card className="p-6">
          <h3 className="font-semibold text-lg mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="justify-start">
              <ArrowUpRight className="w-4 h-4 mr-2" />
              Send Tokens
            </Button>
            <Button variant="outline" className="justify-start">
              <TrendingUp className="w-4 h-4 mr-2" />
              Stake Tokens
            </Button>
          </div>
        </Card>
      )}

      {/* Error Display */}
      {tokenState.error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <p className="text-sm text-red-800">{tokenState.error}</p>
        </Card>
      )}
    </div>
  )
}
