#
# spec file for package supportutils-plugin-pmem
#
# Copyright (c) 2020-2022 SUSE LLC.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/


Name:           supportutils-plugin-pmem
Version:        0.0.1
Release:    	1.1.0
Source: 		supportutils-plugin-pmem-%{version}.tar.bz2 
Summary:        Supportconfig Plugin for pmem
License:        GPL-2.0-only
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
Requires:       supportconfig-plugin-resource
Requires:       supportconfig-plugin-tag
BuildRequires:  %{python_module mimetypes}
BuildRequires:  %{python_module os}
BuildRequires:  %{python_module subproces}
BuildRequires:  %{python_module sys}
BuildRequires:  %{python_module io}
BuildRequires:  %{python_module pathlib}

%description
Extends supportconfig functionality to include system information for
ndctl (NVDIMM) & ipmctl (Intel pmem). The plugin also saves related logs.

%prep
%setup -q
%build

%install
install -d $RPM_BUILD_ROOT/usr/lib/supportconfig/plugins
install -d $RPM_BUILD_ROOT/sbin
install -m 0544  ha_sap $RPM_BUILD_ROOT/usr/lib/supportconfig/plugins

%files
%defattr(-,root,root)
/usr/lib/supportconfig
/usr/lib/supportconfig/plugins
/usr/lib/supportconfig/plugins/pmem.py

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Mar  9 2022 rangelino@suse.com
- Initial working version
