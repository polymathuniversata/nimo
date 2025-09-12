import { cva, type VariantProps } from "class-variance-authority"

export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-semibold ring-offset-background transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 active:scale-95",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-button hover:shadow-button-hover",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-button hover:shadow-button-hover",
        outline:
          "border-2 border-input bg-background hover:bg-accent hover:text-accent-foreground hover:border-accent-foreground/20 shadow-sm hover:shadow-hover",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-button hover:shadow-button-hover",
        ghost: "hover:bg-accent hover:text-accent-foreground hover:shadow-sm",
        link: "text-primary underline-offset-4 hover:underline hover:text-primary/80",
        gradient: "bg-gradient-to-r from-primary to-secondary text-white hover:from-primary/90 hover:to-secondary/90 shadow-glow hover:shadow-glow-hover",
        success: "bg-green-500 text-white hover:bg-green-600 shadow-button hover:shadow-button-hover",
        warning: "bg-yellow-500 text-white hover:bg-yellow-600 shadow-button hover:shadow-button-hover",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3 text-xs",
        lg: "h-12 rounded-lg px-8 text-base",
        xl: "h-14 rounded-xl px-10 text-lg",
        icon: "h-10 w-10",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-12 w-12",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

export type { VariantProps }