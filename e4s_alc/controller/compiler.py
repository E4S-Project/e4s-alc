class Compiler:
    package_name_to_compiler_name = {
        "llvm": "clang",
        "intel-oneapi-compilers": "oneapi",
        "llvm-amdgpu": "rocmcc",
        "intel-oneapi-compilers-classic": "intel",
        "acfl": "arm",
    }
    
    def __init__(self, spack_compiler):
        self.spack_compiler = spack_compiler
        self.compiler, self.package, self.version, self.version_suffix = self.get_compiler_info()

    def get_compiler_info(self):
        compiler, package, version, version_suffix = None, None, None, None

        # Splitting package and version if '@' is present
        if '@' in self.spack_compiler:
            package, version = self.spack_compiler.split('@')
        else:
            package = self.spack_compiler

        # Check if the package name exists in the mapping dictionary

        if package in self.package_name_to_compiler_name.keys():
            compiler = self.package_name_to_compiler_name[package]
        else:
            compiler = package if package else self.spack_compiler

        # Format version suffix
        version_suffix = f'@{version}' if version else ''

        if not version:
            version = 'latest'

        return compiler, package, version, version_suffix


    def get_spack_compiler_commands(self, signature):
        signature_flag = ''
        if not signature:
            signature_flag = '--no-check-signature '

        spack_compiler_commands = [
            'spack compiler find',
            f'spack install {signature_flag}{self.spack_compiler}',
            'spack module tcl refresh -y 1> /dev/null',
            f'. /spack/share/spack/setup-env.sh && spack load {self.spack_compiler} && spack compiler find',
            f'spack config add "packages:all:compiler:[{self.compiler}{self.version_suffix}]"',
            f'spack config add "config:install_missing_compilers:true"'
        ]
        return spack_compiler_commands


