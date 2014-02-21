import platform
import _winreg
import errno
import sys


class RegistryError(Exception):
	pass


class RegistryHkey(object):
	def __init__(self, hkey, arch='process'):
		self._arch_default = False
		self._arch32 = False
		self._arch64 = False
		self._set_arch(arch)

		if hkey in self.valid_hkeys():
			self.hkey = getattr(_winreg, hkey)
			self._hkey_name = hkey
		else:
			raise RegistryError("{} is not one of {}".format(hkey, self.valid_hkeys()))

	def valid_hkeys(self):
		return [x for x in _winreg.__dict__.keys() if x.startswith('HKEY_')]

	def _set_arch(self, arch):
		if arch == 'process':
			self._arch_default = True
		elif int(arch) == 32:
			self._arch32 = True
		elif int(arch) == 64:
			self._arch64 = True
		else:
			raise RegistryError("Architecture must be '32', '64', or 'process', not {}".format(arch))

	def get_key_value(self, path, value_name):
		with self._readable_key(path) as key:
			if not self.has_value(key):
				raise RegistryError(r"'{}\{}' has no value to get.".format(self._hkey_name, path))

			return _winreg.QueryValueEx(key, value_name)

	def get_values(self, path):
		value_names = {}
		with self._readable_key(path) as key:
			count = 0
			while True:
				try:
					value = _winreg.EnumValue(key, count)
					value_names[value[0]] = value[1]
				except WindowsError:
					break
				count += 1
			return value_names

	def has_value(self, key):
		return _winreg.QueryInfoKey(key)[1] > 0

	def key_exists(self, key):
		try:
			key = _winreg.OpenKey(self.hkey, key)
			_winreg.CloseKey(key)
			return True
		except WindowsError as e:
			if e.errno == errno.ENOENT:
				return False
			else:
				raise

	def set_value(self, path, value_name, value, create=True):
		with self._writable_key(path, create=create) as key:
			_winreg.SetValueEx(key, value_name, 0, _winreg.REG_SZ, value)

	@property
	def arch32(self):
		return self._arch32

	@arch32.setter
	def arch32(self, value):
		if value:
			self._arch_default = False
			self._arch64 = False
			self._arch32 = True
		else:
			self._arch32 = False

	@property
	def arch64(self):
		return self._arch64

	@arch64.setter
	def arch64(self, value):
		if value:
			self._arch_default = False
			self._arch32 = False
			self._arch64 = True
		else:
			self._arch64 = False

	@property
	def arch_default(self):
		return self._arch_default

	@arch_default.setter
	def arch_default(self, value):
		if value:
			self._arch32 = False
			self._arch64 = False
			self._arch_default = True
		else:
			self._arch_default = value

	@property
	def _architecture(self):
		assert [self.arch_default, self.arch32, self.arch64].count(True) == 1, "Invalid state.  Only one architecture " \
		                                                                       "can be active at a a time."
		if self.arch_default:
			return 0
		elif self.arch32:
			return _winreg.KEY_WOW64_32KEY
		elif self.arch64:
			return _winreg.KEY_WOW64_64KEY

		else:
			raise ValueError("One or both of obj.arch32 and obj.arch64 OR obj.arch_default must be set to True.")

	def __key(self, path, create=False, writable=False):
		if create:
			get_key = _winreg.CreateKeyEx
		else:
			get_key = _winreg.OpenKey

		if writable:
			access = _winreg.KEY_ALL_ACCESS
		else:
			access = _winreg.KEY_READ

		try:
			key = get_key(self.hkey, path, 0, self._architecture | access)
		except WindowsError as e:
			if e.errno == errno.EACCES:
				raise RegistryError("The requested action requires write permissions to the registry.")
			else:
				raise
		return key

	def _writable_key(self, path, create=False):
		return self.__key(path, create=create, writable=True)

	def _readable_key(self, path, create=False):
		return self.__key(path, create=create, writable=False)


def is_os_64bit():
	return platform.machine().endswith('64')


def is_python_64bit():
	return sys.maxsize > 2 ** 2
