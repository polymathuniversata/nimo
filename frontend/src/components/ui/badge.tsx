import * as React from "react"
import { cn } from "@/lib/utils"
import { badgeVariants, type BadgeProps } from "./badge-variants"

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge }
