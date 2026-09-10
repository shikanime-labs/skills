# Extensibility

Source: Tasks/extensibility index, EnvoyPatchPolicy, extension server.

EG offers several extension paths beyond built-in features.

## Access Envoy features not in the API

- **Envoy Patch Policy** (`envoy-patch-policy`) — directly modify Envoy xDS
  configuration. Lowest-level escape hatch.
- **Extension Server** (`extension-server`) — external gRPC service that
  transforms xDS configuration.

## Custom processing logic

- **WASM Extensions** (`wasm`) — WebAssembly modules for high-performance
  custom logic. `build-wasm-image` task builds the image.
- **External Processing** (`ext-proc`) — call external gRPC services during
  request processing.
- **Lua Extensions** (`lua`) — lightweight scripting.
- **Dynamic Modules** (`dynamic-modules`) — load custom C++ modules at runtime.
- **Remote Infrastructure Provider** (`remote-infrastructure-provider`) — defer
  Envoy data plane management to a custom infra provider.
- **OPA Sidecar with Unix Domain Socket** (`opa-sidecar-unix-domain-socket`).

## Where configured

- `EnvoyExtensionPolicy` targets `Gateway`, `Route`, `Backend` for WASM /
  ext-proc / Lua / dynamic modules.
- `EnvoyPatchPolicy` targets `GatewayClass`/`Gateway` for raw xDS patches.
- `Backend` enables routing to external processes over Unix Domain Sockets.

## Reference page

Tasks/extensibility lists all: envoy-patch-policy, extension-server, ext-proc,
wasm, build-wasm-image, lua, dynamic-modules, remote-infrastructure-provider,
opa-sidecar-unix-domain-socket.
