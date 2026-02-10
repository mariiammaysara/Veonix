import { ApiError } from "./api";

export interface UserFriendlyError {
    title: string;
    message: string;
}

export function getUserFriendlyError(error: any): UserFriendlyError {
    // Log the real error for debugging
    console.error("Global Error Handler Caught:", error);

    // Default fallback
    const defaultError: UserFriendlyError = {
        title: "Something went wrong",
        message: "Please try again later."
    };

    if (!error) return defaultError;

    // Handle ApiError (custom class we created)
    if (error instanceof ApiError) {
        if (error.status === 503) {
            return {
                title: "AI Service Busy",
                message: "The AI is busy right now. Please try again in a moment."
            };
        }

        if (error.status === 400) {
            return {
                title: "Invalid Request",
                message: "We couldn’t process this request. Please check your input."
            };
        }

        if (error.status === 413) {
            return {
                title: "File Too Large",
                message: "The image is too large. Please upload a smaller one."
            };
        }
    }

    // Handle String messages or Error objects
    const errorMessage = (error.message || error.toString()).toLowerCase();

    // Network / Connection errors
    if (
        errorMessage.includes("network") ||
        errorMessage.includes("failed to fetch") ||
        errorMessage.includes("connection")
    ) {
        return {
            title: "Connection Problem",
            message: "Connection problem. Check your internet and try again."
        };
    }

    // Invalid Image specific keywords (if backend returns text in 400/422 that wasn't caught above)
    if (
        errorMessage.includes("image") ||
        errorMessage.includes("unsupported") ||
        errorMessage.includes("format")
    ) {
        return {
            title: "Invalid Image",
            message: "We couldn’t read this image. Please try another one."
        };
    }

    return defaultError;
}
