from spirit_extras import calculation_folder, dependency_gatherer
from importlib.machinery import SourceFileLoader
from datetime import datetime
import pprint
import traceback
import __paths__
import os


class Fig_Dispatcher:
    def __init__(self, folder):
        self.folder = folder

        self._log = "log" in self.folder

        if self._log:
            self._log_path = self.process_path(folder["log"])
            log_dir = os.path.dirname(self._log_path)
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)

    def process_path(self, input_string):
        # __paths__ file
        for possible_path in __paths__._choices:
            pattern = "{" + f"__paths__.{possible_path}" + "}"
            if pattern in input_string:
                input_string = input_string.replace(
                    pattern, __paths__._main(possible_path)
                )

        # {__this__}
        pattern = "{__this__}"
        if pattern in input_string:
            input_string = input_string.replace(pattern, str(self.folder))

        input_string = os.path.normpath(self.folder.to_abspath(input_string))
        return input_string

    def dict_to_module_vars(self, module, input_dict):
        for key, val in input_dict.items():
            varname = f"{key.upper()}_"
            setattr(module, varname, val)
            self.log(f"setting {varname} = {val}\n")

    def log(self, msg):
        if self._log:
            with open(self._log_path, "a") as L:
                L.write(msg)

    def function_from_module_string(self, input_string, module_identifier):
        module_name, function_name = input_string.split(".")
        module_path = self.process_path(module_name + ".py")
        self.log(f"Loading module = {module_path}\n")

        module = SourceFileLoader(module_identifier, module_path).load_module()
        func = getattr(module, function_name)
        return module, func

    def gather_dependencies(self, folder):
        if not "depends" in folder:
            return

        dep_gatherer = dependency_gatherer.Dependency_Gatherer(self.verbose)

        for dependency_name, dependency_dict in folder["depends"].items():
            self.log(f"Adding dependency: `{dependency_name}`\n")
            self.log(pprint.pformat(dependency_dict) + "\n")

            if "output_files" in dependency_dict:
                dependency_paths = dependency_dict["output_files"]

                if not type(dependency_paths) == list:
                    raise Exception(
                        "In dependency `{}`: `output_files` has to given as a list (even for single paths)".format(
                            dependency_name
                        )
                    )

                self.log(f"Before: {dependency_paths}\n")
                for i, p in enumerate(dependency_paths):
                    dependency_paths[i] = self.process_path(p)

                self.log(f"After: {dependency_paths}\n")

            cb = dependency_dict.get("callback", None)
            self.log(f"callback function = {cb}\n")

            if type(cb) == str:
                module, cb_func = self.function_from_module_string(
                    cb, module_identifier=dependency_name
                )
                self.dict_to_module_vars(module, dependency_dict)
                self.dict_to_module_vars(module, folder.get("meta", dict()))
            else:
                cb_func = None

            dep_gatherer.depends(
                dependency_paths,
                cb_func,
                always_generate = dependency_dict.get("always_generate", False),
            )
            self.log("---\n")

        self.log(f"Checking dependencies ...\n")
        dep_gatherer.check()

    def create_figure(self, folder):
        if not "figure" in folder:
            raise Exception("No `figure` field")
        figure_dict = folder["figure"]

        if not "script" in figure_dict:
            raise Exception("`script` field in `figure` has to be specified")
        if not "output_file" in figure_dict:
            raise Exception("`output_file` field in `figure` has to be specified")

        module, figure_func = self.function_from_module_string(
            figure_dict["script"], module_identifier="figure.module.name"
        )

        figure_dict["output_file"] = self.process_path(figure_dict["output_file"])

        self.log(f"Figure output file: `{figure_dict['output_file']}`")
        self.dict_to_module_vars(module, figure_dict)
        self.dict_to_module_vars(module, folder.get("meta", dict()))

        dict_of_dependency_files = {}
        for key, val in folder.get("depends",{}).items():
            dict_of_dependency_files[key] = val["output_files"]

        self.dict_to_module_vars(module, dict_of_dependency_files)

        dep_gatherer = dependency_gatherer.Dependency_Gatherer(self.verbose)
        dep_gatherer.depends(figure_dict["output_file"])
        figure_func()
        dep_gatherer.check()


def main(path, verbose):

    folder = calculation_folder.Calculation_Folder(
        path, create=False, descriptor_file="descriptor.yaml"
    )

    dispatcher = Fig_Dispatcher(folder)
    dispatcher.verbose = verbose

    dispatcher.log(f"{80*'='}\n")
    dispatcher.log(f"{str(datetime.now()):^80}\n")
    dispatcher.log(f"{80*'='}\n")

    try:
        dispatcher.log(f"{60*'-'}\n")
        dispatcher.log(f"{'Gathering dependencies':^60}\n")
        dispatcher.log(f"{60*'-'}\n")

        dispatcher.gather_dependencies(folder)

        dispatcher.log(f"{60*'-'}\n")
        dispatcher.log(f"{'Creating figure':^60}\n")
        dispatcher.log(f"{60*'-'}\n")

        dispatcher.create_figure(folder)

        dispatcher.log(f"{80*'-'}\n")
        dispatcher.log(f"{'SUCCESSFULLY FINISHED':^80}\n")
        dispatcher.log(f"{80*'='}\n")
    except Exception as e:
        dispatcher.log("Exception: {}\n".format(str(e)))
        dispatcher.log(traceback.format_exc() + "\n")
        raise e


if __name__ == "__main__":
    import argparse as argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("folders", nargs="+")
    parser.add_argument("-v", action="store_true")

    args = parser.parse_args()

    for path in args.folders:
        main(path, args.v)
