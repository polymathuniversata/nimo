import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<
  HTMLInputElement,
  React.ComponentProps<"input"> & {
    variant?: 'default' | 'filled' | 'outlined'
    error?: boolean
  }
>(
  ({ className, type, variant = 'default', error = false, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm transition-all duration-200 ease-out",
          {
            'border-input focus-visible:ring-ring': variant === 'default' && !error,
            'border-0 bg-muted/50 focus-visible:ring-ring focus-visible:bg-background': variant === 'filled' && !error,
            'border-2 border-border focus-visible:ring-ring focus-visible:border-ring': variant === 'outlined' && !error,
            'border-destructive focus-visible:ring-destructive': error,
          },
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
