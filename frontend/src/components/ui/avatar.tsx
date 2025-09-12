import * as React from "react"
import * as AvatarPrimitive from "@radix-ui/react-avatar"

import { cn } from "@/lib/utils"

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root> & {
    variant?: 'default' | 'ring' | 'gradient'
    size?: 'sm' | 'default' | 'lg' | 'xl'
  }
>(({ className, variant = 'default', size = 'default', ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex shrink-0 overflow-hidden rounded-full transition-all duration-200 ease-out hover:scale-105",
      {
        'h-8 w-8': size === 'sm',
        'h-10 w-10': size === 'default',
        'h-12 w-12': size === 'lg',
        'h-16 w-16': size === 'xl',
        'ring-2 ring-offset-2 ring-ring ring-offset-background': variant === 'ring',
        'ring-2 ring-offset-2 ring-primary/20 ring-offset-background': variant === 'gradient',
      },
      className
    )}
    {...props}
  />
))
Avatar.displayName = AvatarPrimitive.Root.displayName

const AvatarImage = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Image>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image
    ref={ref}
    className={cn("aspect-square h-full w-full object-cover", className)}
    {...props}
  />
))
AvatarImage.displayName = AvatarPrimitive.Image.displayName

const AvatarFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Fallback>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn(
      "flex h-full w-full items-center justify-center rounded-full bg-muted text-sm font-semibold text-muted-foreground transition-colors duration-200 ease-out hover:bg-muted/80",
      className
    )}
    {...props}
  />
))
AvatarFallback.displayName = AvatarPrimitive.Fallback.displayName

export { Avatar, AvatarImage, AvatarFallback }
