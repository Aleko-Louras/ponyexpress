//An api inspired by class examples that connect to the backend



class ApiError extends Error {
    constructor(status, { error, message }) {
        super(message);
        this.status = status;
        this.code = error;
    }
}

const baseUrl = "http://localhost:8000";

const handleResponse = async (response) => {
    if (response.ok) {
        return response.status === 204 ? {} : await response.json();
    } else {
        const error = await response.json();
        if (error.detail) {
            throw new ApiError(response.status, {
                error: "validation",
                message: JSON.stringify(error.detail),
            });
        } else {
            throw new ApiError(response.status, error);
        }
    }
};

const get = async (url, headers = {}) => {
    const response = await fetch(baseUrl + url, {
        method: "GET",
        headers,
        credentials: "include",
    });
    return handleResponse(response);
};

const post = async (url, headers = {}, data = {}) => {
    const response = await fetch(baseUrl + url, {
        method: "POST",
        headers: {
            ...headers,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include",
    });
    return handleResponse(response);
};

const put = async (url, headers = {}, data = {}) => {
    const response = await fetch(baseUrl + url, {
        method: "PUT",
        headers: {
            ...headers,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include",
    });
    return handleResponse(response);
};

const postForm = async (url, headers = {}, data = {}) => {
    const response = await fetch(baseUrl + url, {
        method: "POST",
        headers: {
            ...headers,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(data),
        credentials: "include",
    });
    return handleResponse(response);
};

const putForm = async (url, headers = {}, data = {}) => {
    const response = await fetch(baseUrl + url, {
        method: "PUT",
        headers: {
            ...headers,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(data),
        credentials: "include",
    });
    return handleResponse(response);
};

const deleteRequest = async (url, headers = {}) => {
    const response = await fetch(baseUrl + url, {
        method: "DELETE",
        headers,
        credentials: "include",
    });
    return handleResponse(response);
};

export default {
    get,
    post,
    postForm,
    put,
    putForm,
    delete: deleteRequest,
};
