{
  flake = {
    homeModules = {
      default = import ../home/default.nix;
      skills = import ../home/default.nix;
    };
  };
}
