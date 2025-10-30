export const useToast = () => {
  return {
    toasts: [],
    toast: (options: any) => console.log('Toast:', options)
  }
}