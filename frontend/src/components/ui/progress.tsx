import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"

import { cn } from "@/lib/utils"

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> & {
    variant?: 'default' | 'gradient' | 'striped'
    size?: 'sm' | 'default' | 'lg'
  }
>(({ className, value, variant = 'default', size = 'default', ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn(
      "relative w-full overflow-hidden rounded-full bg-secondary transition-all duration-300 ease-out",
      {
        'h-2': size === 'sm',
        'h-4': size === 'default',
        'h-6': size === 'lg',
      },
      className
    )}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className={cn(
        "h-full w-full flex-1 transition-all duration-500 ease-out",
        {
          'bg-primary': variant === 'default',
          'bg-gradient-to-r from-primary to-secondary': variant === 'gradient',
          'bg-primary relative overflow-hidden': variant === 'striped',
        }
      )}
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
    >
      {variant === 'striped' && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
      )}
    </ProgressPrimitive.Indicator>
  </ProgressPrimitive.Root>
))
Progress.displayName = ProgressPrimitive.Root.displayName

export { Progress }
