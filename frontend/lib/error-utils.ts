/**
 * Veonix — Error Utilities
 * lib/error-utils.ts
 *
 * Maps ApiError codes to user-friendly messages.
 * All error display logic lives here — never inline in components.
 */

import { ApiError } from "./api";

export interface UserFriendlyError {
    title: string;
    message: string;
}

const ERROR_MAP: Record<string, UserFriendlyError> = {
    INVALID_IMAGE_FORMAT: {
        title: "Invalid Image",
        message: "Please upload a JPEG, PNG, or WEBP image.",
    },
    IMAGE_TOO_LARGE: {
        title: "Image Too Large",
        message: "Please upload an image under 10MB.",
    },
    IMAGE_CORRUPTED: {
        title: "Corrupted Image",
        message: "The image appears to be corrupted. Try a different photo.",
    },
    VISION_SERVICE_UNAVAILABLE: {
        title: "AI Unavailable",
        message: "The AI service is temporarily unavailable. Please try again.",
    },
    LOW_CONFIDENCE: {
        title: "Unclear Image",
        message: "Couldn't identify the food. Try a clearer photo with better lighting.",
    },
    NO_FOOD_DETECTED: {
        title: "No Food Found",
        message: "No food was detected. Please upload a photo of a meal.",
    },
    NUTRITION_NOT_FOUND: {
        title: "Nutrition Unavailable",
        message: "Couldn't find nutrition data for this food.",
    },
    INTERNAL_ERROR: {
        title: "Server Error",
        message: "Something went wrong on our end. Please try again.",
    },
};

export function getUserFriendlyError(error: unknown): UserFriendlyError {
    if (error instanceof ApiError) {
        // Use mapped message if available
        if (ERROR_MAP[error.code]) return ERROR_MAP[error.code];

        // HTTP status fallbacks
        if (error.status === 503)
            return { title: "Service Unavailable", message: "Please try again in a moment." };
        if (error.status === 429)
            return { title: "Too Many Requests", message: "Please wait before trying again." };
        if (error.status >= 500)
            return { title: "Server Error", message: "Something went wrong. Please try again." };

        return { title: "Error", message: error.message };
    }

    // Network errors
    if (error instanceof TypeError && error.message.includes("fetch")) {
        return {
            title: "Connection Error",
            message: "Could not reach the server. Check your internet connection.",
        };
    }

    return {
        title: "Something Went Wrong",
        message: "An unexpected error occurred. Please try again.",
    };
}
