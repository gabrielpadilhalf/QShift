import { AtmText } from "../AtmText/index.js";

/**
 * MolLoadingPage – loading page
 */
export function MolLoadingPage() {
    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4" />
                <AtmText size="sm" color="muted">Loading...</AtmText>
            </div>
        </div>
    );
}