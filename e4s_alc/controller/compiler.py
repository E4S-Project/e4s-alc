from e4s_alc.util import log_function_call, log_info, log_error

class Compiler:
    """Represents a compiler with associated package name and version info.

    Attributes:
        spack_compiler (str): The compiler name parsed by spack.
        compiler (str): The actual compiler name.
        package (str): The name of the compiler package.
        version (str): The version associated with the compiler.
        version_suffix (str): The version suffix formed by '@' and the version.
    """

    PACKAGE_TO_COMPILER = {
        "llvm": "clang",
        "intel-oneapi-compilers": "oneapi",
        "llvm-amdgpu": "rocmcc",
        "intel-oneapi-compilers-classic": "intel",
        "acfl": "arm",
    }

    @log_function_call
    def __init__(self, spack_compiler, backend):
        """Initialize Compiler instance with spack compiler name string.

        Args:
            spack_compiler (str): The compiler name as parsed by spack.
        """
        self.spack_compiler = spack_compiler
        self.backend = backend
        self.compiler, self.package, self.version, self.version_suffix = self._parse_compiler_info()

    @log_function_call
    def _parse_compiler_info(self):
        """Parse spack compiler name into compiler, package, version, and version suffix.

        Returns:
            tuple: The compiler, package, version, and version suffix information.
        """
        compiler, package, version, version_suffix = None, None, None, None
        spack_compiler_no_dep, dependency = self.spack_compiler.split(" ") if " " in self.spack_compiler else (self.spack_compiler, None)
        package, version = spack_compiler_no_dep.split("@") if "@" in self.spack_compiler else (self.spack_compiler, None)
        log_info(f"Determined package: {package}, version: {version}.")

        compiler = self.PACKAGE_TO_COMPILER.get(package, package or self.spack_compiler)
        compiler = ' '.join([compiler, dependency])
        log_info(f"Determined compiler: {compiler}.")

        version_suffix = f"@{version}" if version else ""
        version = version if version else "latest"
        log_info(f"Final version: {version}.")

        return compiler, package, version, version_suffix

    @log_function_call
    def get_spack_compiler_commands(self, signature):
        """Generate compiler commands needed for the spack.

        Args:
            signature (str): The signature associated with the spack.

        Returns:
            list: The list of spack compiler commands.
        """
        signature_flag = "" if signature else "--no-check-signature "
        spack_compiler_commands = [
            "spack compiler find",
            f"spack install {signature_flag}{self.spack_compiler}",
            "spack module tcl refresh -y 1> /dev/null"]
        if self.backend != "singularity":
            spack_compiler_commands = spack_compiler_commands + [f". /spack/share/spack/setup-env.sh && spack load {self.spack_compiler} && spack compiler find",
            f"spack config add 'packages:all:compiler:[{self.compiler}{self.version_suffix}]'"]

        return spack_compiler_commands
