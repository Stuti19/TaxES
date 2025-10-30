import * as React from "react"

const Toast = ({ children, ...props }: any) => <div {...props}>{children}</div>
const ToastClose = () => <button>×</button>
const ToastDescription = ({ children }: any) => <div>{children}</div>
const ToastProvider = ({ children }: any) => <>{children}</>
const ToastTitle = ({ children }: any) => <div>{children}</div>
const ToastViewport = () => <div />

export { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport }