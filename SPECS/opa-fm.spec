# One of the steps this package's insane build system does is patching version
# strings in built binaries (MakeTools/patch_version/patch_version.c).
# The expected template of a version string (ICS_BUILD_VERSION from
# CodeVersion/code_version.c) is not found in binaries that contain a
# GetCodeVersion() call. I suspect LTO optimizes it away.
# Disabling LTO made the build work.
%global _lto_cflags %{nil}

Name: opa-fm
Epoch: 1
Version: 10.11.2.0.3
Release: 1%{?dist}
Summary: Intel Omni-Path Fabric Management Software

License: GPLv2 or BSD
Url: https://github.com/cornelisnetworks/opa-fm
Source0: https://github.com/cornelisnetworks/opa-fm/archive/refs/tags/v%{version}.tar.gz

# bz1262327 needs Patch0002
Patch0002: 0001-Fix-well-known-tempfile-issue-in-script.patch
Patch0003: opafm-link-all-executables-with-pie.patch
Patch0004: add-fPIC-flag.patch

BuildRequires: openssl-devel, expat-devel
BuildRequires: libibverbs-devel >= 1.2.0
BuildRequires: libibumad-devel
BuildRequires: zlib-devel
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: systemd-rpm-macros
Requires: libhfi1
ExclusiveArch: x86_64

%description
opa-fm contains Intel Omni-Path fabric management applications. This
includes: the Subnet Manager, Baseboard Manager, Performance Manager,
Fabric Executive, and some fabric management tools.

%prep
%setup -q
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1

# Make it possible to override hardcoded compiler flags
sed -i -r -e 's/(release_C(C)?OPT_Flags\s*)=/\1?=/' Makerules/Target.LINUX.GNU.*
sed -r -e 's/(^COPT\s*=\s*)/#\1/' -i Esm/ib/src/linux/opafmvf/Makefile

%build
export CFLAGS='%{optflags} -std=gnu11'
export CXXFLAGS='%{optflags} -std=gnu11'
export release_COPT_Flags='%{optflags} -std=gnu11'
export release_CCOPT_Flags='%{optflags} -std=gnu11'
cd Esm
OPA_FEATURE_SET=opa10 ./fmbuild $BUILD_ARGS

%install
BUILDDIR=%{_builddir} DESTDIR=%{buildroot} LIBDIR=%{_libdir} RPM_INS=n ./Esm/fm_install.sh
chmod 644 %{buildroot}/%{_unitdir}/opafm.service
mkdir -p %{buildroot}/%{_localstatedir}/usr/lib/opa-fm/
chmod a-x %{buildroot}/%{_prefix}/share/opa-fm/opafm_src.xml

%post
%systemd_post opafm.service

%preun
%systemd_preun opafm.service

%postun
%systemd_postun_with_restart opafm.service

%files
%doc Esm/README
%{_unitdir}/opafm.service
%config(noreplace) %{_sysconfdir}/opa-fm/opafm.xml
%config(noreplace) %{_sysconfdir}/opa-fm/opafm_pp.xml
%{_sysconfdir}/opa-fm
%{_prefix}/lib/opa-fm/bin/*
%{_prefix}/lib/opa-fm/runtime/*
%{_prefix}/share/opa-fm/*
%{_sbindir}/opafmcmd
%{_sbindir}/opafmcmdall
%{_sbindir}/opafmconfigpp
%{_sbindir}/opafmvf
%{_mandir}/man8/*

%changelog
* Wed Feb 08 2023 Michal Schmidt <mschmidt@redhat.com> - 10.11.2.0.3-1
- Update to upstream version 10.11.2.0.3
- Resolves: rhbz#2110931

* Tue May 25 2021 Honggang Li <honli@redhat.com> - 10.11.0.2.1-1
- Rebase to upstream release 10.11.0.2.1
- Resolves: bz1921701, bz1959990

* Thu Nov 12 2020 Honggang Li <honli@redhat.com> - 10.10.3.0.11-1
- Rebase to upstream release 10.10.3.0.11
- Resolves: bz1821735

* Wed Apr 15 2020 Honggang Li <honli@redhat.com> - 10.10.1.0.35-1
- Rebase to upstream release 10.10.1.0.35
- Resolves:bz1739281

* Tue Dec 03 2019 Honggang Li <honli@redhat.com> - 10.10.0.0.444-2
- Override hard-coded CFLAGS for opafmvf
- Resolves bz1778557

* Thu Oct 31 2019 Honggang Li <honli@redhat.com> - 10.10.0.0.444-1
- Rebase to upstream release 10.10.0.0.444
- Resolves:bz1719674

* Tue Jun 11 2019 Honggang Li <honli@redhat.com> - 10.9.2.2.1-1
- Rebase to upstream release 10.9.2.2.1
- Resolves: bz1660617

* Wed Sep 26 2018 Honggang Li <honli@redhat.com> - 10.7.0.0.145-2
- Link all executables with '-pie'
- Resovles: bz1624155

* Wed Jun 13 2018 Honggang Li <honli@redhat.com> - 10.7.0.0.145-1
- Rebase to latest upstream release
- Resolves: bz1581530

* Tue Dec 12 2017 Honggang Li <honli@redhat.com> - 10.5.1.0.1-2
- Don't include obsolete header bits/sigset.h
- Resolves: bz1523732

* Thu Oct 19 2017 Honggang Li <honli@redhat.com> - 10.5.1.0.1-1
- Rebase to upstream release 10.5.1.0.1
- Resolves: bz1452787, bz1500903

* Fri Mar 17 2017 Honggang Li <honli@redhat.com> - 10.3.1.0-8
- Rebase to upstream branch v10_3_1 as required.
- Clean up change log.
- Apply Epoch tag.
- Resolves: bz1257452, bz1382792

* Sun Jul 10 2016 Honggang Li <honli@redhat.com> - 10.1.0.0-145
- Rebase to latest upstream release.
- Related: bz1273151

* Tue Jun 21 2016 Honggang Li <honli@redhat.com> - 10.0.1.0-4
- Create private state dir.
- Resolves: bz1348477

* Thu Jun  2 2016 Honggang Li <honli@redhat.com> - 10.0.1.0-3
- Requires libhfi1.
- Remove executable permission bit of opafm.service.
- Resolves: bz1341971

* Thu May 26 2016 Honggang Li <honli@redhat.com> - 10.0.1.0-2
- Rebase to upstream release 10.0.1.0.
- Related: bz1273151

* Mon Sep 28 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-444
- Update the N-V-R
- Related: bz1262327

* Mon Sep 28 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-443
- Apply one missed patch to fix various /tmp races
- Revert the script for building (S)RPMs
- Resolves: bz1262327

* Thu Sep 24 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-442
- Fix typo in changelog
- Related: bz1262327

* Wed Sep 23 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-441
- Fix various /tmp races
- Resolves: bz1262327

* Wed Aug 26 2015 Michal Schmidt <mschmidt@redhat.com> - 10.0.0.0-440
- Respect optflags.
- Avoid overflowing prog path due to /opt -> /usr/lib substitution.
- Resolves: bz1257087
- Resolves: bz1257093

* Mon Aug 24 2015 Michal Schmidt <mschmidt@redhat.com> - 10.0.0.0-439
- Update to new upstream snapshot with unbundled expat.
- Related: bz1173302

* Tue Aug 18 2015 Michal Schmidt <mschmidt@redhat.com> - 10.0.0.0-438
- Initial packaging for RHEL, based on upstream spec file.
- Cleaned up spec.
- Moved /opt/opafm -> /usr/lib/opa-fm.
- Fix scriptlets.

* Thu Oct 09 2014 Kaike Wan <kaike.wan@intel.com> - 10.0.0.0-177
- Initial version
