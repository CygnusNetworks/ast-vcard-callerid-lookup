%if 0%{?rhel} && 0%{?rhel} <= 7
%{!?py2_build: %global py2_build %{__python2} setup.py build}
%{!?py2_install: %global py2_install %{__python2} setup.py install --skip-build --root %{buildroot}}
%endif

%if (0%{?fedora} >= 21 || 0%{?rhel} >= 8)
%global with_python3 1
%endif

%define srcname astvcardcallerid
%define version 0.10
%define release 1
%define sum Cygnus Networks GmbH %{srcname} package

Name:           python-%{srcname}
Version:        %{version}
Release:        %{release}%{?dist}
Summary:        %{sum}
License:        proprietary
Source0:        python-%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel, python-setuptools

%{?systemd_requires}
BuildRequires: systemd

%if 0%{?with_check}
BuildRequires:  pytest
%endif # with_check
Requires:       python-setuptools, python-configobj, python-pyst, python-phonenumbers, python-vobject

%{?python_provide:%python_provide python-%{project}}

%description
%{sum}

%prep
%setup -q -n python-%{srcname}-%{version}

%build
%py2_build

%install
%py2_install
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{srcname}
install -p -m 644 ./%{srcname}.service $RPM_BUILD_ROOT%{_unitdir}/%{srcname}.service

%post
%systemd_post astvcardcallerid.service

%preun
%systemd_preun astvcardcallerid.service

%postun
%systemd_postun_with_restart astvcardcallerid.service

%files
%dir %{python2_sitelib}/%{srcname}

%{_bindir}/%{srcname}
%{_datadir}/%{srcname}
%{_unitdir}/%{srcname}.service
%{python2_sitelib}/%{srcname}/*.*
%{python2_sitelib}/%{srcname}-%{version}-py2.*.egg-info

%changelog
