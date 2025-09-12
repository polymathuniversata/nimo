import * as React from "react"
import * as CheckboxPrimitive from "@radix-ui/react-checkbox"
import { Check } from "lucide-react"

import { cn } from "@/lib/utils"

const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root> & {
    variant?: 'default' | 'rounded' | 'square'
    size?: 'sm' | 'default' | 'lg'
  }
>(({ className, variant = 'default', size = 'default', ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      "peer shrink-0 border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 ease-out hover:border-primary/80",
      {
        'h-4 w-4 rounded-sm data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'default' && size === 'default',
        'h-3 w-3 rounded-sm data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'default' && size === 'sm',
        'h-5 w-5 rounded-sm data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'default' && size === 'lg',
        'h-4 w-4 rounded-full data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'rounded' && size === 'default',
        'h-3 w-3 rounded-full data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'rounded' && size === 'sm',
        'h-5 w-5 rounded-full data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'rounded' && size === 'lg',
        'h-4 w-4 rounded-none data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'square' && size === 'default',
        'h-3 w-3 rounded-none data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'square' && size === 'sm',
        'h-5 w-5 rounded-none data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground': variant === 'square' && size === 'lg',
      },
      className
    )}
    {...props}
  >
    <CheckboxPrimitive.Indicator
      className={cn("flex items-center justify-center text-current animate-in fade-in-0 zoom-in-95 duration-200")}
    >
      <Check className={cn({
        'h-4 w-4': size === 'default',
        'h-3 w-3': size === 'sm',
        'h-5 w-5': size === 'lg',
      })} />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
))
Checkbox.displayName = CheckboxPrimitive.Root.displayName

export { Checkbox }
