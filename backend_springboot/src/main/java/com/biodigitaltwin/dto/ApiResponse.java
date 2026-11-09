package com.biodigitaltwin.dto;

import java.time.LocalDateTime;

/**
 * Envelope for every API response: status, message, payload and server timestamp.
 *
 * @param <T> payload type
 */
public record ApiResponse<T>(int status, String message, T data, LocalDateTime timestamp) {

    /**
     * Builds a success envelope stamped with the current time.
     *
     * @param data payload to return
     * @param message human-readable result message
     * @param <T> payload type
     * @return response with status 200
     */
    public static <T> ApiResponse<T> success(T data, String message) {
        return new ApiResponse<>(200, message, data, LocalDateTime.now());
    }

    /**
     * Builds an error envelope with no payload.
     *
     * @param status HTTP-like status code of the failure
     * @param message error description shown to the client
     * @param <T> payload type, always {@code null} here
     * @return response carrying the given status and message
     */
    public static <T> ApiResponse<T> error(int status, String message) {
        return new ApiResponse<>(status, message, null, LocalDateTime.now());
    }
}
