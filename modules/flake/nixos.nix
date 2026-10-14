{
  flake = {
    nixosModules = {
      default = import ../nixos/default.nix;
      skills = import ../nixos/default.nix;
    };
  };
}
