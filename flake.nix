{
  description = "adversial ai class";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: 

  let 
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in
  {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        pkgs.maven
        pkgs.python312
        pkgs.python312Packages.sh
        pkgs.android-tools
        pkgs.apktool
        pkgs.jadx
        pkgs.jdk8
        pkgs.stdenv.cc.cc.lib
        pkgs.llvm_18
      ];
      LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
      SHELL="${pkgs.bashInteractive}/bin/bash";
      ANDROID_HOME="${pkgs.android-tools}";
    };

  };
}
