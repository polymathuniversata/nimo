import * as React from "react"
import * as SwitchPrimitives from "@radix-ui/react-switch"

import { cn } from "@/lib/utils"

const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitives.Root> & {
    variant?: 'default' | 'gradient' | 'minimal'
    size?: 'sm' | 'default' | 'lg'
  }
>(({ className, variant = 'default', size = 'default', ...props }, ref) => (
  <SwitchPrimitives.Root
    className={cn(
      "peer inline-flex shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-all duration-300 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50",
      {
        'h-5 w-9 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input': variant === 'default' && size === 'sm',
        'h-6 w-11 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input': variant === 'default' && size === 'default',
        'h-7 w-13 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input': variant === 'default' && size === 'lg',
        'h-6 w-11 data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-primary data-[state=checked]:to-secondary data-[state=unchecked]:bg-input': variant === 'gradient' && size === 'default',
        'h-5 w-9 data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-primary data-[state=checked]:to-secondary data-[state=unchecked]:bg-input': variant === 'gradient' && size === 'sm',
        'h-7 w-13 data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-primary data-[state=checked]:to-secondary data-[state=unchecked]:bg-input': variant === 'gradient' && size === 'lg',
        'h-6 w-11 data-[state=checked]:bg-primary data-[state=unchecked]:bg-muted border-muted-foreground/20': variant === 'minimal' && size === 'default',
        'h-5 w-9 data-[state=checked]:bg-primary data-[state=unchecked]:bg-muted border-muted-foreground/20': variant === 'minimal' && size === 'sm',
        'h-7 w-13 data-[state=checked]:bg-primary data-[state=unchecked]:bg-muted border-muted-foreground/20': variant === 'minimal' && size === 'lg',
      },
      className
    )}
    {...props}
    ref={ref}
  >
    <SwitchPrimitives.Thumb
      className={cn(
        "pointer-events-none block rounded-full bg-background shadow-lg ring-0 transition-all duration-300 ease-out",
        {
          'h-4 w-4 data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0': size === 'sm',
          'h-5 w-5 data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0': size === 'default',
          'h-6 w-6 data-[state=checked]:translate-x-6 data-[state=unchecked]:translate-x-0': size === 'lg',
        }
      )}
    />
  </SwitchPrimitives.Root>
))
Switch.displayName = SwitchPrimitives.Root.displayName

export { Switch }
